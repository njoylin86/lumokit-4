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
define( 'LUMOKIT_CSS_OPTION_KEY', 'lumokit_compiled_css' );


// ---------------------------------------------------------------------------
// 1. REST API: /wp-json/lumokit/v1/components
//    GET  – returns all registered components
//    POST – creates or updates a component from a JSON payload
// ---------------------------------------------------------------------------

add_action( 'rest_api_init', 'lumokit_register_routes' );

function lumokit_register_routes() {
	register_rest_route( 'lumokit/v1', '/styles', [
		[
			'methods'             => WP_REST_Server::CREATABLE,
			'callback'            => 'lumokit_save_styles',
			'permission_callback' => 'lumokit_auth_check',
		],
	] );

	register_rest_route( 'lumokit/v1', '/site', [
		[
			'methods'             => WP_REST_Server::CREATABLE,
			'callback'            => 'lumokit_build_site',
			'permission_callback' => 'lumokit_auth_check',
		],
	] );

	register_rest_route( 'lumokit/v1', '/pages', [
		[
			'methods'             => WP_REST_Server::CREATABLE,
			'callback'            => 'lumokit_build_page',
			'permission_callback' => 'lumokit_auth_check',
		],
	] );

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
 * POST /wp-json/lumokit/v1/site
 * Creates multiple pages and a nav menu in one request.
 *
 * Expected JSON body:
 * {
 *   "site_name": "Boxmedia",
 *   "pages": [
 *     { "title": "Hem", "slug": "hem", "menu_label": "Start", "blocks": ["lumo/hero-section"] },
 *     { "title": "Kontakt", "slug": "kontakt", "menu_label": "Kontakt", "blocks": ["lumo/contact-form"] }
 *   ]
 * }
 */
function lumokit_build_site( WP_REST_Request $request ) {
	$body = $request->get_json_params();

	if ( empty( $body['site_name'] ) || empty( $body['pages'] ) || ! is_array( $body['pages'] ) ) {
		return new WP_Error( 'missing_field', 'Required fields missing: site_name, pages', [ 'status' => 400 ] );
	}

	$site_name  = sanitize_text_field( $body['site_name'] );
	$pages_spec = $body['pages'];
	$results    = [];

	// --- Create or update each page ---
	foreach ( $pages_spec as $page_spec ) {
		if ( empty( $page_spec['title'] ) || empty( $page_spec['blocks'] ) ) {
			continue;
		}

		$page_request = new WP_REST_Request( 'POST' );
		$page_request->set_body( wp_json_encode( [
			'title'  => $page_spec['title'],
			'slug'   => $page_spec['slug'] ?? sanitize_title( $page_spec['title'] ),
			'blocks' => $page_spec['blocks'],
		] ) );
		$page_request->set_header( 'content-type', 'application/json' );

		$page_response = lumokit_build_page( $page_request );

		if ( is_wp_error( $page_response ) ) {
			return $page_response;
		}

		$results[] = $page_response->get_data();
	}

	// --- Create or update the nav menu ---
	$menu_name = $site_name . ' — Primär meny';
	$menu_id   = wp_get_nav_menu_object( $menu_name );

	if ( $menu_id ) {
		$menu_id = $menu_id->term_id;
		// Remove existing items so we can rebuild in correct order
		$existing_items = wp_get_nav_menu_items( $menu_id );
		if ( $existing_items ) {
			foreach ( $existing_items as $item ) {
				wp_delete_post( $item->ID, true );
			}
		}
	} else {
		$menu_id = wp_create_nav_menu( $menu_name );
		if ( is_wp_error( $menu_id ) ) {
			return new WP_Error( 'menu_failed', $menu_id->get_error_message(), [ 'status' => 500 ] );
		}
	}

	// --- Add menu items in order ---
	foreach ( $pages_spec as $page_spec ) {
		$slug  = $page_spec['slug'] ?? sanitize_title( $page_spec['title'] );
		$page  = get_page_by_path( $slug, OBJECT, 'page' );
		$label = $page_spec['menu_label'] ?? $page_spec['title'];

		if ( ! $page ) {
			continue;
		}

		wp_update_nav_menu_item( $menu_id, 0, [
			'menu-item-title'     => $label,
			'menu-item-object'    => 'page',
			'menu-item-object-id' => $page->ID,
			'menu-item-type'      => 'post_type',
			'menu-item-status'    => 'publish',
		] );
	}

	// --- Assign menu to lumokit-primary location ---
	$locations                    = get_theme_mod( 'nav_menu_locations', [] );
	$locations['lumokit-primary'] = $menu_id;
	set_theme_mod( 'nav_menu_locations', $locations );

	return rest_ensure_response( [
		'success'   => true,
		'menu_id'   => $menu_id,
		'pages'     => $results,
		'message'   => 'Site built with ' . count( $results ) . ' page(s) and menu assigned.',
	] );
}

/**
 * POST /wp-json/lumokit/v1/pages
 * Creates a WordPress page and populates it with the specified LumoKit blocks in order.
 *
 * Expected JSON body:
 * {
 *   "title":  "Hem",
 *   "slug":   "hem",           // optional
 *   "blocks": ["lumo/hero-section", "lumo/services-row", ...]
 * }
 */
function lumokit_build_page( WP_REST_Request $request ) {
	$body = $request->get_json_params();

	if ( empty( $body['title'] ) || empty( $body['blocks'] ) || ! is_array( $body['blocks'] ) ) {
		return new WP_Error( 'missing_field', 'Required fields missing: title, blocks', [ 'status' => 400 ] );
	}

	$title      = sanitize_text_field( $body['title'] );
	$slug       = ! empty( $body['slug'] ) ? sanitize_title( $body['slug'] ) : sanitize_title( $title );
	$block_names = $body['blocks'];

	// Validate that all referenced blocks exist
	$components = get_option( LUMOKIT_OPTION_KEY, [] );
	$missing    = [];
	foreach ( $block_names as $block_name ) {
		if ( ! isset( $components[ $block_name ] ) ) {
			$missing[] = $block_name;
		}
	}
	if ( ! empty( $missing ) ) {
		return new WP_Error(
			'blocks_not_found',
			'The following blocks are not registered: ' . implode( ', ', $missing ),
			[ 'status' => 400 ]
		);
	}

	// Build Gutenberg block markup
	$content_parts = [];
	foreach ( $block_names as $block_name ) {
		$short_name = lumokit_block_short_name( $block_name );
		$block_id   = 'block_' . uniqid();
		$content_parts[] = sprintf(
			'<!-- wp:acf/%s {"id":"%s","name":"acf/%s","mode":"preview"} /-->',
			$short_name,
			$block_id,
			$short_name
		);
	}
	$post_content = implode( "\n", $content_parts );

	// Check if a page with this slug already exists
	$existing = get_page_by_path( $slug, OBJECT, 'page' );

	if ( $existing ) {
		$page_id = wp_update_post( [
			'ID'           => $existing->ID,
			'post_title'   => $title,
			'post_content' => $post_content,
			'post_status'  => 'publish',
		], true );
		$action = 'updated';
	} else {
		$page_id = wp_insert_post( [
			'post_type'    => 'page',
			'post_title'   => $title,
			'post_name'    => $slug,
			'post_content' => $post_content,
			'post_status'  => 'publish',
		], true );
		$action = 'created';
	}

	if ( is_wp_error( $page_id ) ) {
		return new WP_Error( 'page_failed', $page_id->get_error_message(), [ 'status' => 500 ] );
	}

	return rest_ensure_response( [
		'success'  => true,
		'page_id'  => $page_id,
		'page_url' => get_permalink( $page_id ),
		'edit_url' => admin_url( 'post.php?post=' . $page_id . '&action=edit' ),
		'message'  => 'Page ' . $action . ' with ' . count( $block_names ) . ' block(s).',
	] );
}

/**
 * POST /wp-json/lumokit/v1/styles
 * Receives compiled Tailwind CSS and stores it in wp_options.
 */
function lumokit_save_styles( WP_REST_Request $request ) {
	$body = $request->get_json_params();

	if ( empty( $body['css'] ) ) {
		return new WP_Error( 'missing_field', 'Required field missing: css', [ 'status' => 400 ] );
	}

	update_option( LUMOKIT_CSS_OPTION_KEY, $body['css'], false );

	return rest_ensure_response( [
		'success' => true,
		'message' => 'Stylesheet saved.',
	] );
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
//      a) A Gutenberg block via acf_register_block_type()  (skipped for header/footer)
//      b) A local field group via acf_add_local_field_group()
//    Special components lumo/site-header and lumo/site-footer are registered
//    on an ACF Options Page instead of as Gutenberg blocks.
// ---------------------------------------------------------------------------

// Reserved block names that are injected globally, not used as Gutenberg blocks
define( 'LUMOKIT_INJECTED', [ 'lumo/site-header', 'lumo/site-footer' ] );

add_action( 'acf/init', 'lumokit_register_dynamic_blocks' );

function lumokit_register_dynamic_blocks() {
	if ( ! function_exists( 'acf_register_block_type' ) ) {
		return;
	}

	// Register ACF Options Page for header/footer editing
	if ( function_exists( 'acf_add_options_page' ) ) {
		acf_add_options_page( [
			'page_title' => 'LumoKit — Header & Footer',
			'menu_title' => 'Header & Footer',
			'menu_slug'  => 'lumokit-global',
			'capability' => 'edit_posts',
			'icon_url'   => 'dashicons-star-filled',
		] );
	}

	$components = get_option( LUMOKIT_OPTION_KEY, [] );

	foreach ( $components as $component ) {
		$block_name = $component['block_name'];
		$schema     = $component['schema'];

		if ( empty( $block_name ) || ! is_array( $schema ) ) {
			continue;
		}

		$fields     = lumokit_schema_to_acf_fields( $schema, $block_name );
		$group_key  = 'group_lumo_' . sanitize_title( str_replace( '/', '_', $block_name ) );

		if ( in_array( $block_name, LUMOKIT_INJECTED, true ) ) {
			// Register field group on the Options Page
			acf_add_local_field_group( [
				'key'      => $group_key,
				'title'    => $component['title'] . ' Fields',
				'fields'   => $fields,
				'location' => [
					[
						[
							'param'    => 'options_page',
							'operator' => '==',
							'value'    => 'lumokit-global',
						],
					],
				],
			] );
		} else {
			// Register as a normal Gutenberg block
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

			acf_add_local_field_group( [
				'key'      => $group_key,
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
		$name    = sanitize_key( $field_def['name'] ?? '' );
		$type    = $field_def['type'] ?? 'text';
		$default = $field_def['default'] ?? '';
		$value   = get_field( $name );

		if ( $type === 'image' && is_array( $value ) ) {
			$value = $value['url'] ?? '';
		}

		// Fall back to schema default when ACF field is empty
		if ( empty( $value ) && ! empty( $default ) ) {
			$value = $default;
		}

		// Fall back to placeholder image if still empty
		if ( $type === 'image' && empty( $value ) ) {
			$value = 'https://placehold.co/800x600';
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
// 4. Register nav menu locations
// ---------------------------------------------------------------------------

add_action( 'init', 'lumokit_register_menus' );

function lumokit_register_menus() {
	register_nav_menus( [
		'lumokit-primary' => 'LumoKit — Primär meny',
	] );
}


// ---------------------------------------------------------------------------
// 5. Strip theme header/footer via output buffering
// ---------------------------------------------------------------------------

add_action( 'template_redirect', 'lumokit_start_buffer' );

function lumokit_start_buffer() {
	ob_start( 'lumokit_strip_theme_chrome' );
}

function lumokit_strip_theme_chrome( $html ) {
	// Remove BlankSlate's <header id="header">...</header>
	$html = preg_replace( '/<header\s[^>]*id=["\']header["\'][^>]*>.*?<\/header>/is', '', $html );
	// Remove BlankSlate's <footer id="footer">...</footer>
	$html = preg_replace( '/<footer\s[^>]*id=["\']footer["\'][^>]*>.*?<\/footer>/is', '', $html );
	// Remove page title header (<header class="header">)
	$html = preg_replace( '/<header\s[^>]*class=["\']header["\'][^>]*>.*?<\/header>/is', '', $html );
	return $html;
}


// ---------------------------------------------------------------------------
// 5. Inject Header & Footer on every page
// ---------------------------------------------------------------------------

add_action( 'wp_body_open', 'lumokit_inject_header' );
add_action( 'wp_footer',    'lumokit_inject_footer' );

function lumokit_inject_header() {
	lumokit_render_injected( 'lumo/site-header' );
}

function lumokit_inject_footer() {
	lumokit_render_injected( 'lumo/site-footer' );
}

/**
 * Renders a globally injected component (header/footer) using ACF options values.
 * Falls back to schema defaults when no option value is set.
 */
function lumokit_render_injected( $block_name ) {
	$components = get_option( LUMOKIT_OPTION_KEY, [] );

	if ( ! isset( $components[ $block_name ] ) ) {
		return;
	}

	$component     = $components[ $block_name ];
	$html_template = $component['html_template'];
	$schema        = $component['schema'];

	if ( empty( $html_template ) || ! is_array( $schema ) ) {
		return;
	}

	$replacements = [];

	foreach ( $schema as $field_def ) {
		$name    = sanitize_key( $field_def['name'] ?? '' );
		$type    = $field_def['type'] ?? 'text';
		$default = $field_def['default'] ?? '';

		if ( $type === 'nav_menu' ) {
			// Render a WordPress nav menu — the field name is the theme_location
			$value = wp_nav_menu( [
				'theme_location' => $name,
				'container'      => false,
				'menu_class'     => '',
				'fallback_cb'    => false,
				'echo'           => false,
				'items_wrap'     => '%3$s',
			] );
			$replacements[ '{{' . $name . '}}' ] = $value ?: '';
			continue;
		}

		// Read from ACF Options Page
		$value = function_exists( 'get_field' ) ? get_field( $name, 'option' ) : '';

		if ( $type === 'image' && is_array( $value ) ) {
			$value = $value['url'] ?? '';
		}

		if ( empty( $value ) && ! empty( $default ) ) {
			$value = $default;
		}

		if ( $type === 'image' && empty( $value ) ) {
			$value = 'https://placehold.co/800x200';
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
// 6. Enqueue compiled Tailwind CSS on the frontend
// ---------------------------------------------------------------------------

add_action( 'wp_head', 'lumokit_output_styles' );

function lumokit_output_styles() {
	$css = get_option( LUMOKIT_CSS_OPTION_KEY, '' );
	echo '<style id="lumokit-styles">' . $css . '</style>' . "\n";
	echo '<style id="lumokit-reset">body{margin:0;}</style>' . "\n";
}


// ---------------------------------------------------------------------------
// 5. Register a custom block category for LumoKit blocks in the editor
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
