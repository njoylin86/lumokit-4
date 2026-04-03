<?php
/**
 * Plugin Name: LumoKit Bridge
 * Description: Data-Driven Component Engine. Receives JSON payloads from the LumoKit AI pipeline
 *              and dynamically registers ACF field groups and Gutenberg blocks.
 * Version:     1.1.0
 * Author:      LumoKit
 */

defined( 'ABSPATH' ) || exit;

define( 'LUMOKIT_OPTION_KEY', 'lumokit_components' );


// ---------------------------------------------------------------------------
// 1. REST API: /wp-json/lumokit/v1/components
//    GET  – returns all registered components
//    POST – creates or updates a component from a JSON payload
// ---------------------------------------------------------------------------

add_action( 'rest_api_init', 'lumokit_register_routes' );

function lumokit_register_routes() {
	register_rest_route( 'lumokit/v1', '/components', [
		[
			'methods'             => WP_REST_Server::READABLE,
			'callback'            => 'lumokit_get_components',
			'permission_callback' => 'lumokit_auth_check',
		],
		[
			'methods'             => WP_REST_Server::CREATABLE,
			'callback'            => 'lumokit_save_component',
			'permission_callback' => 'lumokit_auth_check',
		],
	] );
}

function lumokit_auth_check() {
	return current_user_can( 'edit_posts' );
}

/**
 * GET /wp-json/lumokit/v1/components
 */
function lumokit_get_components( WP_REST_Request $request ) {
	$components = get_option( LUMOKIT_OPTION_KEY, [] );
	return rest_ensure_response( array_values( $components ) );
}

/**
 * POST /wp-json/lumokit/v1/components
 *
 * Expected JSON body:
 * {
 *   "block_name":    "lumo/hero-section",
 *   "title":         "Hero Section",
 *   "html_template": "<section>...</section>",
 *   "schema":        [ { "name": "headline", "type": "text", "label": "Rubrik" }, … ]
 * }
 */
function lumokit_save_component( WP_REST_Request $request ) {
	$body = $request->get_json_params();

	$required = [ 'block_name', 'title', 'html_template', 'schema' ];
	foreach ( $required as $field ) {
		if ( empty( $body[ $field ] ) ) {
			return new WP_Error(
				'missing_field',
				sprintf( 'Required field missing: %s', $field ),
				[ 'status' => 400 ]
			);
		}
	}

	$block_name    = sanitize_text_field( $body['block_name'] );
	$title         = sanitize_text_field( $body['title'] );
	$html_template = $body['html_template'];
	$schema        = $body['schema'];

	$components = get_option( LUMOKIT_OPTION_KEY, [] );
	$is_update  = isset( $components[ $block_name ] );

	$components[ $block_name ] = [
		'block_name'    => $block_name,
		'title'         => $title,
		'html_template' => $html_template,
		'schema'        => $schema,
	];

	update_option( LUMOKIT_OPTION_KEY, $components, false );

	return rest_ensure_response( [
		'success'    => true,
		'block_name' => $block_name,
		'message'    => $is_update ? 'Component updated.' : 'Component created.',
	] );
}


// ---------------------------------------------------------------------------
// 2. Dynamic ACF & Block Registration
//    Runs on acf/init – loops all saved components and registers:
//      a) A Gutenberg block via acf_register_block_type()
//      b) A local field group via acf_add_local_field_group()
// ---------------------------------------------------------------------------

add_action( 'acf/init', 'lumokit_register_dynamic_blocks' );

function lumokit_register_dynamic_blocks() {
	if ( ! function_exists( 'acf_register_block_type' ) ) {
		return;
	}

	$components = get_option( LUMOKIT_OPTION_KEY, [] );

	foreach ( $components as $component ) {
		$block_name    = $component['block_name'];
		$schema        = $component['schema'];

		if ( empty( $block_name ) || ! is_array( $schema ) ) {
			continue;
		}

		acf_register_block_type( [
			'name'            => lumokit_block_short_name( $block_name ),
			'title'           => $component['title'],
			'render_callback' => 'lumokit_render_block',
			'category'        => 'lumokit',
			'icon'            => 'star-filled',
			'keywords'        => [ 'lumokit', 'component' ],
			'mode'            => 'preview',
			'supports'        => [ 'align' => false, 'mode' => false ],
		] );

		$fields = lumokit_schema_to_acf_fields( $schema, $block_name );

		acf_add_local_field_group( [
			'key'      => 'group_lumo_' . sanitize_title( str_replace( '/', '_', $block_name ) ),
			'title'    => $component['title'] . ' Fields',
			'fields'   => $fields,
			'location' => [
				[
					[
						'param'    => 'block',
						'operator' => '==',
						'value'    => 'acf/' . lumokit_block_short_name( $block_name ),
					],
				],
			],
		] );
	}
}

function lumokit_block_short_name( $block_name ) {
	$parts = explode( '/', $block_name );
	return end( $parts );
}

function lumokit_schema_to_acf_fields( array $schema, $block_name ) {
	$fields      = [];
	$slug_prefix = sanitize_title( str_replace( '/', '_', $block_name ) );

	foreach ( $schema as $field_def ) {
		$name  = sanitize_key( $field_def['name'] );
		$type  = $field_def['type'] ?? 'text';
		$label = sanitize_text_field( $field_def['label'] ?? $name );

		$allowed_types = [ 'text', 'textarea', 'image', 'url' ];
		if ( ! in_array( $type, $allowed_types, true ) ) {
			$type = 'text';
		}

		$fields[] = [
			'key'   => 'field_' . $slug_prefix . '_' . $name,
			'name'  => $name,
			'label' => $label,
			'type'  => $type,
		];
	}

	return $fields;
}


// ---------------------------------------------------------------------------
// 3. Block Render Callback
// ---------------------------------------------------------------------------

function lumokit_render_block( $block, $content = '', $is_preview = false ) {
	// Derive block_name from the ACF block name: "acf/hero-section" → "lumo/hero-section"
	$short_name = str_replace( 'acf/', '', $block['name'] );
	$block_name = 'lumo/' . $short_name;

	$components = get_option( LUMOKIT_OPTION_KEY, [] );

	if ( ! isset( $components[ $block_name ] ) ) {
		if ( $is_preview ) {
			echo '<p style="color:red;">[LumoKit] Component not found: ' . esc_html( $block_name ) . '</p>';
		}
		return;
	}

	$component     = $components[ $block_name ];
	$html_template = $component['html_template'];
	$schema        = $component['schema'];

	if ( empty( $html_template ) || ! is_array( $schema ) ) {
		if ( $is_preview ) {
			echo '<p style="color:orange;">[LumoKit] Component template is empty.</p>';
		}
		return;
	}

	$replacements = [];

	foreach ( $schema as $field_def ) {
		$name  = sanitize_key( $field_def['name'] ?? '' );
		$type  = $field_def['type'] ?? 'text';
		$value = get_field( $name );

		if ( $type === 'image' && is_array( $value ) ) {
			$value = $value['url'] ?? '';
		}

		$replacements[ '{{' . $name . '}}' ] = $value ?? '';
	}

	$output = str_replace(
		array_keys( $replacements ),
		array_values( $replacements ),
		$html_template
	);

	// phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped
	echo $output;
}


// ---------------------------------------------------------------------------
// 4. Register a custom block category for LumoKit blocks in the editor
// ---------------------------------------------------------------------------

add_filter( 'block_categories_all', 'lumokit_register_block_category', 10, 2 );

function lumokit_register_block_category( $categories, $post ) {
	return array_merge(
		[
			[
				'slug'  => 'lumokit',
				'title' => 'LumoKit Components',
				'icon'  => null,
			],
		],
		$categories
	);
}
