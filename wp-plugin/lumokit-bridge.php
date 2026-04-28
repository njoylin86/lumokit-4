<?php
/**
 * Plugin Name: LumoKit Bridge
 * Description: Data-Driven Component Engine. Receives JSON payloads from the LumoKit AI pipeline
 *              and dynamically registers ACF field groups and Gutenberg blocks.
 * Version:     1.1.0
 * Author:      LumoKit
 */

defined( 'ABSPATH' ) || exit;

// Single source of truth for bridge version. Bumped by tools/release.py.
define( 'LUMOKIT_BRIDGE_VERSION', '1.0.0' );

define( 'LUMOKIT_OPTION_KEY', 'lumokit_components' );

// Maps override field keys → their component's html_template (for editor pre-population)
$GLOBALS['lumokit_override_templates'] = [];
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

	register_rest_route( 'lumokit/v1', '/settings', [
		[
			'methods'             => WP_REST_Server::CREATABLE,
			'callback'            => 'lumokit_save_settings',
			'permission_callback' => 'lumokit_auth_check',
		],
	] );

	register_rest_route( 'lumokit/v1', '/options', [
		[
			'methods'             => WP_REST_Server::CREATABLE,
			'callback'            => 'lumokit_save_options',
			'permission_callback' => 'lumokit_auth_check',
		],
	] );

	// Public contact-form submission endpoint — no auth, basic spam protection.
	// Version endpoint — public, used by tools/build_all.py to record what's deployed.
	register_rest_route( 'lumokit/v1', '/version', [
		[
			'methods'             => WP_REST_Server::READABLE,
			'callback'            => function () {
				return rest_ensure_response( [
					'bridge_version' => defined( 'LUMOKIT_BRIDGE_VERSION' ) ? LUMOKIT_BRIDGE_VERSION : '0.0.0',
					'wp_version'     => get_bloginfo( 'version' ),
				] );
			},
			'permission_callback' => '__return_true',
		],
	] );

	register_rest_route( 'lumokit/v1', '/contact', [
		[
			'methods'             => WP_REST_Server::CREATABLE,
			'callback'            => 'lumokit_handle_contact',
			'permission_callback' => '__return_true',
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

	// ---------------------------------------------------------------------------
	// WP Code snippet management: /wp-json/lumokit/v1/snippets
	// GET  – list all snippets created by LumoKit
	// POST – create or update a snippet (upsert by title)
	// ---------------------------------------------------------------------------
	register_rest_route( 'lumokit/v1', '/snippets', [
		[
			'methods'             => WP_REST_Server::READABLE,
			'callback'            => 'lumokit_get_snippets',
			'permission_callback' => 'lumokit_auth_check',
		],
		[
			'methods'             => WP_REST_Server::CREATABLE,
			'callback'            => 'lumokit_save_snippet',
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

	// --- Add menu items in order, with optional dropdown support ---
	// First pass: create parent group items (custom links) for any menu_parent values.
	$parent_item_ids = []; // [ 'Tjänster' => 42, ... ]

	foreach ( $pages_spec as $page_spec ) {
		$parent_label = ! empty( $page_spec['menu_parent'] )
			? sanitize_text_field( $page_spec['menu_parent'] )
			: null;

		if ( $parent_label && ! isset( $parent_item_ids[ $parent_label ] ) ) {
			$parent_item_ids[ $parent_label ] = wp_update_nav_menu_item( $menu_id, 0, [
				'menu-item-title'  => $parent_label,
				'menu-item-url'    => '#',
				'menu-item-type'   => 'custom',
				'menu-item-status' => 'publish',
			] );
		}
	}

	// Second pass: create page items, nested under parent when menu_parent is set.
	foreach ( $pages_spec as $page_spec ) {
		$label = ! empty( $page_spec['menu_label'] ) ? $page_spec['menu_label'] : null;

		// Skip pages with no menu_label and no menu_parent — they are not in the menu.
		if ( empty( $label ) && empty( $page_spec['menu_parent'] ) ) {
			continue;
		}

		$slug = $page_spec['slug'] ?? sanitize_title( $page_spec['title'] );
		$page = get_page_by_path( $slug, OBJECT, 'page' );

		if ( ! $page ) {
			continue;
		}

		$item_args = [
			'menu-item-title'     => $label ?? $page_spec['title'],
			'menu-item-object'    => 'page',
			'menu-item-object-id' => $page->ID,
			'menu-item-type'      => 'post_type',
			'menu-item-status'    => 'publish',
		];

		$parent_label = ! empty( $page_spec['menu_parent'] )
			? sanitize_text_field( $page_spec['menu_parent'] )
			: null;

		if ( $parent_label && isset( $parent_item_ids[ $parent_label ] ) ) {
			$item_args['menu-item-parent-id'] = $parent_item_ids[ $parent_label ];
		}

		wp_update_nav_menu_item( $menu_id, 0, $item_args );
	}

	// Third pass: append custom-URL items (e.g. anchor CTAs like "Boka tid").
	$extra_items = ! empty( $body['extra_menu_items'] ) && is_array( $body['extra_menu_items'] )
		? $body['extra_menu_items']
		: [];

	foreach ( $extra_items as $extra ) {
		if ( empty( $extra['label'] ) || empty( $extra['url'] ) ) {
			continue;
		}
		wp_update_nav_menu_item( $menu_id, 0, [
			'menu-item-title'  => sanitize_text_field( $extra['label'] ),
			'menu-item-url'    => esc_url_raw( $extra['url'] ),
			'menu-item-type'   => 'custom',
			'menu-item-status' => 'publish',
		] );
	}

	// --- Assign menu to lumokit-primary location ---
	$locations                    = get_theme_mod( 'nav_menu_locations', [] );
	$locations['lumokit-primary'] = $menu_id;
	set_theme_mod( 'nav_menu_locations', $locations );

	// --- Set the "hem" page as the static front page (so / renders the home page,
	// not the default blog or "Sample Page"). Only acts when a page with slug "hem"
	// was built in this run.
	foreach ( $pages as $page_spec ) {
		if ( ( $page_spec['slug'] ?? '' ) === 'hem' ) {
			$home_page = get_page_by_path( 'hem', OBJECT, 'page' );
			if ( $home_page ) {
				update_option( 'show_on_front', 'page' );
				update_option( 'page_on_front', $home_page->ID );
			}
			break;
		}
	}

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

	// Build Gutenberg block markup. Bake schema defaults into the block's `data`
	// attribute so ACF treats them as saved values from the start. This makes
	// "clear field in WP Admin → field actually disappears" work — without this,
	// the render fallback would always restore defaults and frustrate editors.
	$content_parts = [];
	foreach ( $block_names as $block_name ) {
		$short_name  = lumokit_block_short_name( $block_name );
		$block_id    = 'block_' . uniqid();
		$slug_prefix = sanitize_title( str_replace( '/', '_', $block_name ) );
		$schema      = $components[ $block_name ]['schema'] ?? [];

		$data = new stdClass();
		foreach ( $schema as $field_def ) {
			$name      = sanitize_key( $field_def['name'] ?? '' );
			$type      = $field_def['type'] ?? 'text';
			$default   = $field_def['default'] ?? '';
			$field_key = 'field_' . $slug_prefix . '_' . $name;

			if ( $type === 'nav_menu' ) {
				continue;
			}

			$value_to_bake = $default;
			if ( $type === 'image' ) {
				// ACF expects an attachment ID for image fields. Look it up from the URL
				// in our schema default. If the URL doesn't resolve to a known attachment,
				// skip baking — admin will show "select image" but at least frontend renders.
				if ( ! empty( $default ) && filter_var( $default, FILTER_VALIDATE_URL ) ) {
					$attachment_id = attachment_url_to_postid( $default );
					if ( $attachment_id ) {
						$value_to_bake = $attachment_id;
					} else {
						continue;
					}
				} elseif ( is_numeric( $default ) ) {
					$value_to_bake = (int) $default;
				} else {
					continue;
				}
			}

			$data->{$name}        = $value_to_bake;
			$data->{'_' . $name}  = $field_key;
		}

		$attrs = [
			'id'   => $block_id,
			'name' => 'acf/' . $short_name,
			'data' => $data,
			'mode' => 'preview',
		];

		$content_parts[] = '<!-- wp:acf/' . $short_name . ' ' . wp_json_encode( $attrs, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE ) . ' /-->';
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
 * POST /wp-json/lumokit/v1/settings
 * Stores platform configuration as WP options. Not exposed in WP Admin.
 * Called by build_all.py when bundle contains a "platform_config" section.
 *
 * Accepted fields:
 *   platform               string  e.g. "boxmedia" or "" to clear
 *   trustindex_script      string  raw embed script tag (legacy)
 *   booking_widget_id      string  widget ID/key (legacy boxmedia)
 *   site_reviews_score        string  WordPress shortcode for review score widget
 *   site_reviews_testimonials string  WordPress shortcode for customer reviews/testimonials widget
 *   site_booking_api_key   string  API key for the booking widget
 */
function lumokit_save_settings( WP_REST_Request $request ) {
	$body    = $request->get_json_params();
	$updated = [];

	$allowed = [ 'platform', 'trustindex_script', 'booking_widget_id', 'site_reviews_score', 'site_reviews_testimonials', 'site_booking_api_key', 'site_booking_treatment_id' ];

	foreach ( $allowed as $key ) {
		if ( array_key_exists( $key, $body ) ) {
			update_option( 'lumokit_' . $key, $body[ $key ], false );
			$updated[] = $key;
		}
	}

	// Mirror integration fields to the ACF options namespace (options_{name})
	// so that get_field( 'site_*', 'option' ) and {{site_*}} template variables work.
	if ( array_key_exists( 'trustindex_script', $body ) ) {
		update_option( 'options_site_trustindex_script', $body['trustindex_script'], false );
	}
	if ( array_key_exists( 'booking_widget_id', $body ) ) {
		update_option( 'options_site_booking_widget_id', $body['booking_widget_id'], false );
	}
	if ( array_key_exists( 'site_reviews_score', $body ) ) {
		update_option( 'options_site_reviews_score', $body['site_reviews_score'], false );
	}
	if ( array_key_exists( 'site_reviews_testimonials', $body ) ) {
		update_option( 'options_site_reviews_testimonials', $body['site_reviews_testimonials'], false );
	}
	if ( array_key_exists( 'site_booking_api_key', $body ) ) {
		update_option( 'options_site_booking_api_key', $body['site_booking_api_key'], false );
		// Mirror to the legacy key so existing WP Code snippets reading lumokit_booking_widget_id keep working.
		update_option( 'lumokit_booking_widget_id', $body['site_booking_api_key'], false );
	}
	if ( array_key_exists( 'site_booking_treatment_id', $body ) ) {
		update_option( 'options_site_booking_treatment_id', $body['site_booking_treatment_id'], false );
	}
	// Accept per-page treatment IDs: any key starting with "site_booking_treatment_"
	// is mirrored to ACF options. Allows pushing all 6 treatment IDs in one call.
	foreach ( $body as $key => $value ) {
		if ( is_string( $key ) && strpos( $key, 'site_booking_treatment_' ) === 0
		     && $key !== 'site_booking_treatment_id' ) {
			update_option( 'options_' . $key, $value, false );
			$updated[] = $key;
		}
	}

	return rest_ensure_response( [
		'success' => true,
		'updated' => $updated,
	] );
}


/**
 * POST /wp-json/lumokit/v1/options
 * Sets ACF options page field values (company info etc.).
 * Called by build_all.py when bundle contains a "global_settings" section.
 *
 * Body: { "site_company_name": "Acme AB", "site_phone": "08-123 456", ... }
 */
function lumokit_save_options( WP_REST_Request $request ) {
	if ( ! function_exists( 'update_field' ) ) {
		return new WP_Error( 'acf_missing', 'ACF is not active.', [ 'status' => 500 ] );
	}

	$body    = $request->get_json_params();
	$allowed = [
		'site_company_name',
		'site_address',
		'site_phone',
		'site_email',
		'site_opening_hours',
		'site_facebook',
		'site_instagram',
		'site_linkedin',
		'site_twitter',
		'site_tiktok',
		'site_youtube',
	];
	$updated = [];

	foreach ( $allowed as $key ) {
		if ( array_key_exists( $key, $body ) ) {
			update_field( $key, $body[ $key ], 'option' );
			$updated[] = $key;
		}
	}

	return rest_ensure_response( [
		'success' => true,
		'updated' => $updated,
	] );
}


/**
 * POST /wp-json/lumokit/v1/contact
 * Public endpoint — receives submissions from the native contact form and
 * emails them to the site_email address from ACF options. Basic spam guards:
 *   - Honeypot field "website" must be empty
 *   - Required fields validated
 *   - Throttled per IP via transient (1 submission per 30 seconds)
 */
function lumokit_handle_contact( WP_REST_Request $request ) {
	$body = $request->get_json_params();
	if ( ! is_array( $body ) ) {
		$body = $request->get_params();
	}

	// Honeypot — silently succeed so bots think they got through.
	if ( ! empty( $body['website'] ) ) {
		return rest_ensure_response( [ 'success' => true ] );
	}

	$name    = sanitize_text_field( $body['name'] ?? '' );
	$email   = sanitize_email( $body['email'] ?? '' );
	$phone   = sanitize_text_field( $body['phone'] ?? '' );
	$message = sanitize_textarea_field( $body['message'] ?? '' );

	if ( empty( $name ) || empty( $email ) || empty( $message ) ) {
		return new WP_Error( 'missing_field', 'Namn, e-post och meddelande krävs.', [ 'status' => 400 ] );
	}
	if ( ! is_email( $email ) ) {
		return new WP_Error( 'bad_email', 'Ogiltig e-postadress.', [ 'status' => 400 ] );
	}

	// Rate-limit per IP.
	$ip  = $_SERVER['REMOTE_ADDR'] ?? 'unknown';
	$key = 'lumokit_contact_' . md5( $ip );
	if ( get_transient( $key ) ) {
		return new WP_Error( 'too_fast', 'Vänta en stund innan du skickar igen.', [ 'status' => 429 ] );
	}
	set_transient( $key, 1, 30 );

	// Recipient — site_email from ACF options, falls back to admin_email.
	$to = '';
	if ( function_exists( 'get_field' ) ) {
		$to = get_field( 'site_email', 'option' );
	}
	if ( empty( $to ) ) {
		$to = get_option( 'admin_email' );
	}

	$subject  = '[' . get_bloginfo( 'name' ) . '] Nytt meddelande från ' . $name;
	$body_txt = "Nytt meddelande via kontaktformuläret:\n\n";
	$body_txt .= "Namn: $name\n";
	$body_txt .= "E-post: $email\n";
	if ( ! empty( $phone ) ) {
		$body_txt .= "Telefon: $phone\n";
	}
	$body_txt .= "\nMeddelande:\n$message\n";

	$headers = [
		'Content-Type: text/plain; charset=UTF-8',
		'Reply-To: ' . $name . ' <' . $email . '>',
	];

	$sent = wp_mail( $to, $subject, $body_txt, $headers );

	if ( ! $sent ) {
		return new WP_Error( 'send_failed', 'Vi kunde inte skicka meddelandet just nu. Försök igen senare eller ring oss.', [ 'status' => 500 ] );
	}

	return rest_ensure_response( [ 'success' => true ] );
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

	$required = [ 'block_name', 'title', 'html_template' ];
	foreach ( $required as $field ) {
		if ( empty( $body[ $field ] ) ) {
			return new WP_Error(
				'missing_field',
				sprintf( 'Required field missing: %s', $field ),
				[ 'status' => 400 ]
			);
		}
	}
	// schema is optional — static/design-only components may have no ACF fields
	if ( ! array_key_exists( 'schema', $body ) ) {
		return new WP_Error( 'missing_field', 'Required field missing: schema', [ 'status' => 400 ] );
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
// 1b. WP Code Snippet Management
// ---------------------------------------------------------------------------

/**
 * GET /wp-json/lumokit/v1/snippets
 * Returns all wpcode posts tagged as created by LumoKit.
 */
function lumokit_get_snippets( WP_REST_Request $request ) {
	if ( ! post_type_exists( 'wpcode' ) ) {
		return new WP_Error( 'wpcode_missing', 'WP Code plugin is not active.', [ 'status' => 503 ] );
	}

	$posts = get_posts( [
		'post_type'      => 'wpcode',
		'posts_per_page' => -1,
		'post_status'    => [ 'publish', 'draft' ],
		'meta_key'       => '_lumokit_managed',
		'meta_value'     => '1',
	] );

	$snippets = [];
	foreach ( $posts as $post ) {
		$snippets[] = [
			'id'       => $post->ID,
			'title'    => $post->post_title,
			'location' => get_post_meta( $post->ID, 'wpcode_auto_insert_location', true ),
			'type'     => get_post_meta( $post->ID, 'wpcode_snippet_type', true ),
			'active'   => $post->post_status === 'publish',
		];
	}

	return rest_ensure_response( $snippets );
}

/**
 * POST /wp-json/lumokit/v1/snippets
 * Creates or updates a WP Code snippet (upsert by title).
 *
 * Expected JSON body:
 * {
 *   "title":    "Google Tag Manager",
 *   "code":     "<script>...</script>",
 *   "location": "site_wide_header",   // or "site_wide_footer", "after_post", etc.
 *   "type":     "html",               // "html" | "php" | "css" | "js" (default: "html")
 *   "active":   true
 * }
 */
function lumokit_save_snippet( WP_REST_Request $request ) {
	if ( ! post_type_exists( 'wpcode' ) ) {
		return new WP_Error( 'wpcode_missing', 'WP Code plugin is not active.', [ 'status' => 503 ] );
	}

	$body = $request->get_json_params();

	if ( empty( $body['title'] ) || empty( $body['code'] ) ) {
		return new WP_Error( 'missing_field', 'Required fields: title, code', [ 'status' => 400 ] );
	}

	$title    = sanitize_text_field( $body['title'] );
	$code     = $body['code'];
	$location = sanitize_text_field( $body['location'] ?? 'site_wide_header' );
	$type     = sanitize_text_field( $body['type'] ?? 'html' );
	$active   = ! empty( $body['active'] );
	$status   = $active ? 'publish' : 'draft';

	// Upsert: find existing LumoKit-managed snippet with same title
	$existing = get_posts( [
		'post_type'   => 'wpcode',
		'title'       => $title,
		'post_status' => [ 'publish', 'draft' ],
		'numberposts' => 1,
		'meta_key'    => '_lumokit_managed',
		'meta_value'  => '1',
	] );

	$post_id = null;
	$is_update = false;

	// Bypass kses content filters so PHP/HTML snippet code is stored verbatim.
	kses_remove_filters();

	if ( ! empty( $existing ) ) {
		$post_id   = $existing[0]->ID;
		$is_update = true;
		wp_update_post( [
			'ID'           => $post_id,
			'post_content' => $code,
			'post_status'  => $status,
		] );
	} else {
		$post_id = wp_insert_post( [
			'post_title'   => $title,
			'post_content' => $code,
			'post_type'    => 'wpcode',
			'post_status'  => $status,
		] );

		if ( is_wp_error( $post_id ) ) {
			kses_init_filters();
			return new WP_Error( 'insert_failed', $post_id->get_error_message(), [ 'status' => 500 ] );
		}
	}

	kses_init_filters();

	// Set WP Code meta fields
	update_post_meta( $post_id, 'wpcode_snippet_type', $type );
	update_post_meta( $post_id, 'wpcode_auto_insert_location', $location );
	update_post_meta( $post_id, 'wpcode_auto_insert', $active ? 1 : 0 );

	// WP Code also stores snippet type as a taxonomy term (wpcode_type)
	if ( taxonomy_exists( 'wpcode_type' ) ) {
		wp_set_object_terms( $post_id, $type, 'wpcode_type' );
	}

	// Mark as LumoKit-managed so we can filter/list them
	update_post_meta( $post_id, '_lumokit_managed', '1' );

	return rest_ensure_response( [
		'success'   => true,
		'id'        => $post_id,
		'title'     => $title,
		'location'  => $location,
		'active'    => $active,
		'message'   => $is_update ? 'Snippet updated.' : 'Snippet created.',
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

	// Register ACF Options Pages
	if ( function_exists( 'acf_add_options_page' ) ) {
		// Parent menu item
		acf_add_options_page( [
			'page_title' => 'LumoKit',
			'menu_title' => 'LumoKit',
			'menu_slug'  => 'lumokit-menu',
			'capability' => 'edit_posts',
			'icon_url'   => 'dashicons-star-filled',
			'redirect'   => false,
		] );

		// Sub-page: Header & Footer
		acf_add_options_sub_page( [
			'page_title'  => 'LumoKit — Header & Footer',
			'menu_title'  => 'Header & Footer',
			'menu_slug'   => 'lumokit-global',
			'parent_slug' => 'lumokit-menu',
			'capability'  => 'edit_posts',
		] );

		// Sub-page: Global Settings
		acf_add_options_sub_page( [
			'page_title'  => 'LumoKit — Inställningar',
			'menu_title'  => 'Inställningar',
			'menu_slug'   => 'lumokit-settings',
			'parent_slug' => 'lumokit-menu',
			'capability'  => 'edit_posts',
		] );
	}

	// Register global settings fields.
	// Base fields are always shown. Platform-specific fields are appended
	// only when a platform is active — labels are intentionally neutral.
	if ( function_exists( 'acf_add_local_field_group' ) ) {
		$settings_fields = [
			[
				'key'   => 'field_lumo_settings_tab_company',
				'label' => 'Företagsinformation',
				'name'  => '',
				'type'  => 'tab',
			],
			[
				'key'           => 'field_lumo_site_company_name',
				'name'          => 'site_company_name',
				'label'         => 'Företagsnamn',
				'type'          => 'text',
				'default_value' => '',
			],
			[
				'key'           => 'field_lumo_site_address',
				'name'          => 'site_address',
				'label'         => 'Adress',
				'type'          => 'textarea',
				'rows'          => 3,
				'default_value' => '',
			],
			[
				'key'           => 'field_lumo_site_phone',
				'name'          => 'site_phone',
				'label'         => 'Telefon',
				'type'          => 'text',
				'default_value' => '',
			],
			[
				'key'           => 'field_lumo_site_email',
				'name'          => 'site_email',
				'label'         => 'E-post',
				'type'          => 'text',
				'default_value' => '',
			],
			[
				'key'          => 'field_lumo_site_opening_hours',
				'name'         => 'site_opening_hours',
				'label'        => 'Öppettider',
				'type'         => 'textarea',
				'rows'         => 4,
				'default_value' => '',
				'instructions' => 'T.ex. Mån–Fre 08–17, Lör 10–14',
			],
			[
				'key'   => 'field_lumo_settings_tab_social',
				'label' => 'Sociala medier',
				'name'  => '',
				'type'  => 'tab',
			],
			[
				'key'           => 'field_lumo_site_facebook',
				'name'          => 'site_facebook',
				'label'         => 'Facebook',
				'type'          => 'url',
				'default_value' => '',
				'instructions'  => 'Fullständig URL till Facebook-sidan',
			],
			[
				'key'           => 'field_lumo_site_instagram',
				'name'          => 'site_instagram',
				'label'         => 'Instagram',
				'type'          => 'url',
				'default_value' => '',
				'instructions'  => 'Fullständig URL till Instagram-profilen',
			],
			[
				'key'           => 'field_lumo_site_linkedin',
				'name'          => 'site_linkedin',
				'label'         => 'LinkedIn',
				'type'          => 'url',
				'default_value' => '',
				'instructions'  => 'Fullständig URL till LinkedIn-sidan',
			],
			[
				'key'           => 'field_lumo_site_twitter',
				'name'          => 'site_twitter',
				'label'         => 'Twitter / X',
				'type'          => 'url',
				'default_value' => '',
				'instructions'  => 'Fullständig URL till Twitter/X-profilen',
			],
			[
				'key'           => 'field_lumo_site_tiktok',
				'name'          => 'site_tiktok',
				'label'         => 'TikTok',
				'type'          => 'url',
				'default_value' => '',
				'instructions'  => 'Fullständig URL till TikTok-profilen',
			],
			[
				'key'           => 'field_lumo_site_youtube',
				'name'          => 'site_youtube',
				'label'         => 'YouTube',
				'type'          => 'url',
				'default_value' => '',
				'instructions'  => 'Fullständig URL till YouTube-kanalen',
			],
		];

		// Shortcode widgets — always shown, platform-agnostic.
		$settings_fields[] = [
			'key'   => 'field_lumo_settings_tab_widgets',
			'label' => 'Widgets',
			'name'  => '',
			'type'  => 'tab',
		];
		$settings_fields[] = [
			'key'          => 'field_lumo_site_reviews_score',
			'name'         => 'site_reviews_score',
			'label'        => 'Recensioner — Betygswidget (shortcode)',
			'type'         => 'textarea',
			'rows'         => 3,
			'instructions' => 'Shortcode för betygswidgeten (stjärnor/score). Används via {{site_reviews_score}} i designen.',
		];
		$settings_fields[] = [
			'key'          => 'field_lumo_site_reviews_testimonials',
			'name'         => 'site_reviews_testimonials',
			'label'        => 'Recensioner — Kundrecensioner (shortcode)',
			'type'         => 'textarea',
			'rows'         => 3,
			'instructions' => 'Shortcode för kundrecensioner/testimonials. Används via {{site_reviews_testimonials}} i designen.',
		];
		$settings_fields[] = [
			'key'          => 'field_lumo_site_booking_api_key',
			'name'         => 'site_booking_api_key',
			'label'        => 'Bokning — API-nyckel',
			'type'         => 'text',
			'instructions' => 'API-nyckel för bokningswidgeten. Används i komponenter via {{site_booking_api_key}}.',
		];
		$settings_fields[] = [
			'key'          => 'field_lumo_site_booking_treatment_id',
			'name'         => 'site_booking_treatment_id',
			'label'        => 'Bokning — Behandlings-ID (global default)',
			'type'         => 'text',
			'instructions' => 'TDL-behandlings-ID som visas på sidor utan eget ID. Lämna tomt om widgeten bara ska visas på behandlingssidor.',
		];
		// Per-treatment-page IDs. Field name = site_booking_treatment_<slug>
		// (slugar med bindestreck normaliseras till understreck).
		$treatments = [
			'tandimplantat'    => 'Tandimplantat',
			'invisalign'       => 'Invisalign',
			'akuttandvard'     => 'Akuttandvård',
			'basundersokning'  => 'Basundersökning',
			'allman_tandvard'  => 'Allmän tandvård',
			'tandvardsradsla'  => 'Tandvårdsrädsla',
		];
		foreach ( $treatments as $slug => $label ) {
			$settings_fields[] = [
				'key'          => 'field_lumo_site_booking_treatment_' . $slug,
				'name'         => 'site_booking_treatment_' . $slug,
				'label'        => 'Bokning — Behandlings-ID: ' . $label,
				'type'         => 'text',
				'instructions' => 'TDL-behandlings-ID för ' . $label . '-sidan.',
			];
		}

		// Append legacy integration fields when boxmedia platform is active.
		if ( get_option( 'lumokit_platform', '' ) !== '' ) {
			$settings_fields[] = [
				'key'   => 'field_lumo_settings_tab_integrations',
				'label' => 'Integrationer (avancerat)',
				'name'  => '',
				'type'  => 'tab',
			];
			$settings_fields[] = [
				'key'          => 'field_lumo_site_trustindex_script',
				'name'         => 'site_trustindex_script',
				'label'        => 'Recensionswidget — embed-kod',
				'type'         => 'textarea',
				'rows'         => 5,
				'instructions' => 'Rå embed-kod (script-tagg). Används om shortcode-fältet ovan är tomt.',
			];
			$settings_fields[] = [
				'key'          => 'field_lumo_site_booking_widget_id',
				'name'         => 'site_booking_widget_id',
				'label'        => 'Bokningsmodul — ID',
				'type'         => 'text',
				'instructions' => 'ID-nyckel för bokningsmodulen (legacy).',
			];
		}

		acf_add_local_field_group( [
			'key'      => 'group_lumokit_global_settings',
			'title'    => 'Inställningar',
			'fields'   => $settings_fields,
			'location' => [
				[
					[
						'param'    => 'options_page',
						'operator' => '==',
						'value'    => 'lumokit-settings',
					],
				],
			],
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

			// Append HTML override tab — one click in editor opens the raw template for editing
			$override_field_key = 'field_' . $slug_prefix . '_lumo_html_override';
			$GLOBALS['lumokit_override_templates'][ $override_field_key ] = $component['html_template'];

			$fields[] = [
				'key'   => 'field_' . $slug_prefix . '_tab_html',
				'label' => 'HTML',
				'name'  => '',
				'type'  => 'tab',
			];
			$fields[] = [
				'key'          => $override_field_key,
				'name'         => 'lumo_html_override',
				'label'        => 'Block HTML',
				'type'         => 'textarea',
				'rows'         => 25,
				'instructions' => 'Redigera HTML för detta block på denna sida. Lämna tomt för att använda den globala mallen.',
			];

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

	// -------------------------------------------------------------------------
	// Boxmedia: per-page ACF field for booking treatment ID.
	// Only registered when platform is boxmedia.
	// -------------------------------------------------------------------------
	if ( get_option( 'lumokit_platform', '' ) === 'boxmedia' && function_exists( 'acf_add_local_field_group' ) ) {
		acf_add_local_field_group( [
			'key'    => 'group_boxmedia_booking',
			'title'  => 'Bokning',
			'fields' => [
				[
					'key'          => 'field_boxmedia_treatment_id',
					'name'         => 'booking_treatment_id',
					'label'        => 'Treatment ID',
					'type'         => 'number',
					'instructions' => 'Numeriskt ID för behandlingen. Lämna tomt för att visa standardwidgeten utan förvald behandling.',
					'required'     => 0,
					'min'          => '',
					'max'          => '',
					'step'         => 1,
				],
			],
			'location' => [
				[
					[
						'param'    => 'post_type',
						'operator' => '==',
						'value'    => 'page',
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




// ---------------------------------------------------------------------------
// Filter: return default_value when a LumoKit field has no saved value.
// Runs on both frontend (get_field) and in the Gutenberg editor.
// ---------------------------------------------------------------------------

add_filter( 'acf/load_value', 'lumokit_acf_load_default', 10, 3 );

function lumokit_acf_load_default( $value, $post_id, $field ) {
	// HTML override fields: pre-populate with the component's template in the editor
	// so the developer can see and edit it. On the frontend we skip this — empty = use global template.
	if ( isset( $GLOBALS['lumokit_override_templates'][ $field['key'] ] ) ) {
		if ( ( $value === false || $value === null ) && is_admin() ) {
			return $GLOBALS['lumokit_override_templates'][ $field['key'] ];
		}
		return $value;
	}

	if ( ! empty( $value ) ) {
		return $value;
	}
	// Scope to LumoKit fields only (keys start with "field_lumo")
	if ( strpos( $field['key'], 'field_lumo' ) !== 0 ) {
		return $value;
	}
	return ! empty( $field['default_value'] ) ? $field['default_value'] : $value;
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

		// Don't register default_value with ACF — it would silently re-inject the
		// default when a field is cleared, defeating "clear → disappears" behavior.
		// Defaults are baked directly into the block's data attribute by
		// lumokit_build_page() instead (single source of truth).
		$fields[] = [
			'key'           => 'field_' . $slug_prefix . '_' . $name,
			'name'          => $name,
			'label'         => $label,
			'type'          => $type,
			'default_value' => '',
		];
	}

	return $fields;
}


// ---------------------------------------------------------------------------
// 3. Global Settings Helper
//    Returns mustache replacements for all {{site_*}} variables.
//    Available in every component — both regular blocks and header/footer.
// ---------------------------------------------------------------------------

function lumokit_get_global_replacements() {
	// ACF fields from the client-visible options page
	$acf_fields = [
		'site_company_name',
		'site_address',
		'site_phone',
		'site_email',
		'site_opening_hours',
		'site_facebook',
		'site_instagram',
		'site_linkedin',
		'site_twitter',
		'site_tiktok',
		'site_youtube',
	];

	$replacements = [];

	if ( function_exists( 'get_field' ) ) {
		foreach ( $acf_fields as $field ) {
			$value = get_field( $field, 'option' );
			$replacements[ '{{' . $field . '}}' ] = $value ?: '';
		}
	}

	// Platform flag — set by builder, stored as hidden WP option
	$platform = get_option( 'lumokit_platform', '' );

	if ( $platform === 'boxmedia' ) {
		$replacements['{{site_booking_cta_link}}'] = '#tdl-booking-widget';
	} else {
		$replacements['{{site_booking_cta_link}}'] = '#';
	}

	// Shortcode widgets — always resolved, platform-agnostic.
	if ( function_exists( 'get_field' ) ) {
		$reviews_score        = get_field( 'site_reviews_score', 'option' ) ?: '';
		$reviews_testimonials = get_field( 'site_reviews_testimonials', 'option' ) ?: '';
		$replacements['{{site_reviews_score}}']        = $reviews_score ? do_shortcode( $reviews_score ) : '';
		$replacements['{{site_reviews_testimonials}}'] = $reviews_testimonials ? do_shortcode( $reviews_testimonials ) : '';
		$replacements['{{site_booking_api_key}}']      = get_field( 'site_booking_api_key', 'option' ) ?: '';
	}

	// Legacy integration fields — only when platform is active.
	if ( $platform !== '' && function_exists( 'get_field' ) ) {
		$replacements['{{site_trustindex_script}}']  = get_field( 'site_trustindex_script', 'option' ) ?: '';
		$replacements['{{site_booking_widget_id}}']  = get_field( 'site_booking_widget_id', 'option' ) ?: '';
	}

	return $replacements;
}


// ---------------------------------------------------------------------------
// 4. Block Render Callback
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

	// Use per-page HTML override if a developer has saved one for this block instance
	$html_override = get_field( 'lumo_html_override' );
	if ( ! empty( $html_override ) ) {
		$html_template = $html_override;
	}

	$replacements = [];

	// Per-field detection: has the user explicitly saved a value for THIS field?
	// ACF stores block field data keyed by field key (not name) in $block['data'].
	// If the field key is present, the user has saved this field — even an empty
	// value should be respected (editor expects "clear field → disappears").
	$block_data  = is_array( $block['data'] ?? null ) ? $block['data'] : [];
	$slug_prefix = sanitize_title( str_replace( '/', '_', $block_name ) );

	foreach ( $schema as $field_def ) {
		$name    = sanitize_key( $field_def['name'] ?? '' );
		$type    = $field_def['type'] ?? 'text';
		$default = $field_def['default'] ?? '';
		$value   = get_field( $name );

		if ( $type === 'image' && is_array( $value ) ) {
			$value = $value['url'] ?? '';
		}

		// Has user explicitly set this specific field? Check if the field key OR
		// the underscore-prefixed key (ACF's reference marker) exists in block data.
		$field_key      = 'field_' . $slug_prefix . '_' . $name;
		$user_set_field = array_key_exists( $field_key, $block_data )
			|| array_key_exists( '_' . $name, $block_data )
			|| array_key_exists( $name, $block_data );

		// Fall back to schema default ONLY when the user has never saved this field.
		if ( ! $user_set_field && empty( $value ) && ! empty( $default ) ) {
			$value = $default;
		}

		if ( $type === 'image' && empty( $value ) && ! $user_set_field ) {
			$value = 'https://placehold.co/800x600';
		}

		$replacements[ '{{' . $name . '}}' ] = $value ?? '';
	}

	// Merge global {{site_*}} variables — placed AFTER per-field so chained
	// substitution works: a per-field default of "tel:{{site_phone}}" gets the
	// {{site_phone}} resolved on the next iteration of str_replace.
	$replacements = array_merge( $replacements, lumokit_get_global_replacements() );

	$output = str_replace(
		array_keys( $replacements ),
		array_values( $replacements ),
		$html_template
	);

	// Run shortcodes embedded via mustache substitution (e.g. {{site_reviews_testimonials}}
	// expands to "[trustindex …]" which must be processed before echoing).
	$output = do_shortcode( $output );

	// phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped
	echo $output;
}


// ---------------------------------------------------------------------------
// 5. Register nav menu locations
// ---------------------------------------------------------------------------

add_action( 'init', 'lumokit_register_menus' );

function lumokit_register_menus() {
	register_nav_menus( [
		'lumokit-primary' => 'LumoKit — Primär meny',
	] );
}


// ---------------------------------------------------------------------------
// 8. Strip theme header/footer via output buffering
// ---------------------------------------------------------------------------

add_action( 'template_redirect', 'lumokit_start_buffer' );

function lumokit_start_buffer() {
	ob_start( 'lumokit_strip_theme_chrome' );
}

function lumokit_strip_theme_chrome( $html ) {
	// Remove theme headers
	$html = preg_replace( '/<header\s[^>]*id=["\']header["\'][^>]*>.*?<\/header>/is', '', $html );
	$html = preg_replace( '/<header\s[^>]*class=["\']header["\'][^>]*>.*?<\/header>/is', '', $html );
	// Remove theme footers
	$html = preg_replace( '/<footer\s[^>]*id=["\']footer["\'][^>]*>.*?<\/footer>/is', '', $html );
	// Remove sidebars and widget areas (all common patterns)
	$html = preg_replace( '/<aside\b[^>]*>.*?<\/aside>/is', '', $html );
	$html = preg_replace( '/<div\s[^>]*id=["\']sidebar["\'][^>]*>.*?<\/div>/is', '', $html );
	$html = preg_replace( '/<div\s[^>]*id=["\']secondary["\'][^>]*>.*?<\/div>/is', '', $html );
	$html = preg_replace( '/<div\s[^>]*class=["\'][^"\']*widget-area[^"\']*["\'][^>]*>.*?<\/div>/is', '', $html );
	$html = preg_replace( '/<div\s[^>]*class=["\'][^"\']*widgets[^"\']*["\'][^>]*>.*?<\/div>/is', '', $html );
	// Remove empty paragraphs and leftover theme wrappers
	$html = preg_replace( '/<p>\s*<\/p>/is', '', $html );
	return $html;
}


// ---------------------------------------------------------------------------
// 9. Inject Header & Footer on every page
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
				'items_wrap'     => '<ul>%3$s</ul>',
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

	// Merge global {{site_*}} variables — placed AFTER per-field so chained
	// substitution works (see lumokit_render_block for rationale).
	$replacements = array_merge( $replacements, lumokit_get_global_replacements() );

	$output = str_replace(
		array_keys( $replacements ),
		array_values( $replacements ),
		$html_template
	);

	// Run shortcodes embedded via mustache substitution (e.g. {{site_reviews_testimonials}}
	// expands to "[trustindex …]" which must be processed before echoing).
	$output = do_shortcode( $output );

	// phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped
	echo $output;
}


// ---------------------------------------------------------------------------
// 6. Inject global widgets (Trustindex, Booking) on every page
// ---------------------------------------------------------------------------

add_action( 'wp_footer', 'lumokit_inject_global_widgets', 5 );

function lumokit_inject_global_widgets() {
	$has_acf  = function_exists( 'get_field' );
	$platform = get_option( 'lumokit_platform', '' );

	// TDL/Dentneo booking widget: api key acts as the apiToken for the loader.
	// Treatment id is resolved per-page: first try ACF field
	// `site_booking_treatment_<slug>` (one per treatment page), then fall back
	// to the global `site_booking_treatment_id`. Default empty.
	$booking_api_key      = $has_acf ? get_field( 'site_booking_api_key', 'option' ) : '';
	$booking_treatment_id = '';
	if ( $has_acf ) {
		$queried = get_queried_object();
		$slug    = ( $queried instanceof WP_Post ) ? $queried->post_name : '';
		if ( $slug ) {
			$per_page_id = get_field( 'site_booking_treatment_' . str_replace( '-', '_', $slug ), 'option' );
			if ( ! empty( $per_page_id ) ) {
				$booking_treatment_id = $per_page_id;
			}
		}
		if ( empty( $booking_treatment_id ) ) {
			$booking_treatment_id = get_field( 'site_booking_treatment_id', 'option' );
		}
	}
	if ( ! empty( $booking_api_key ) ) {
		$treatment_attr = $booking_treatment_id
			? ' data-treatment="' . esc_attr( $booking_treatment_id ) . '"'
			: '';
		echo '<div id="tdl-booking-widget"' . $treatment_attr . '></div>' . "\n";
		?>
		<script>
		  (function() {
		    var t = document.getElementById('tdl-booking-widget') &&
		            document.getElementById('tdl-booking-widget').dataset.treatment;
		    if (t && window.tdlWidgetConfig) { window.tdlWidgetConfig.treatmentIds = [t]; }
		  })();
		</script>
		<?php
	}

	// Reviews are NOT injected globally — placed manually via {{site_reviews_score}}
	// and {{site_reviews_testimonials}} in the relevant component templates.
}


// ---------------------------------------------------------------------------
// 7. Enqueue compiled Tailwind CSS on the frontend
// ---------------------------------------------------------------------------

add_action( 'wp_head', 'lumokit_inject_booking_head', 1 );

function lumokit_inject_booking_head() {
	if ( ! function_exists( 'get_field' ) ) {
		return;
	}
	$booking_api_key = get_field( 'site_booking_api_key', 'option' );
	if ( empty( $booking_api_key ) ) {
		return;
	}
	?>
	<script async type="module" src="https://booking-widget-prod-nj23eril7a-lz.a.run.app/v2/widgetloader.js"></script>
	<script>
	  window.tdlWidgetConfig = {
	    mode: "embedded",
	    apiToken: <?php echo wp_json_encode( $booking_api_key ); ?>
	  };
	</script>
	<?php
}

add_action( 'wp_head', 'lumokit_output_styles' );

function lumokit_output_styles() {
	$css = get_option( LUMOKIT_CSS_OPTION_KEY, '' );
	echo '<style id="lumokit-styles">' . $css . '</style>' . "\n";
	echo '<style id="lumokit-reset">body{margin:0;}</style>' . "\n";
	echo '<style id="lumokit-nav">
			nav ul{list-style:none!important;margin:0!important;padding:0!important;}
			nav li{display:inline-block!important;position:relative;margin:0 10px!important;}
			nav li:first-child{margin-left:0!important;}
			nav li:last-child{margin-right:0!important;}
			nav a{text-decoration:none;color:inherit!important;}
			nav .sub-menu{
				display:none!important;
				position:absolute;
				top:100%;
				left:0;
				min-width:180px;
				padding:8px 0;
				z-index:1000;
				background:#ffffff;
				border:1px solid rgba(0,0,0,0.08);
				border-radius:4px;
				box-shadow:0 4px 16px rgba(0,0,0,0.1);
			}
			nav li:hover>.sub-menu{display:block!important;}
			nav .sub-menu li{display:block!important;width:100%;margin:0!important;}
			nav .sub-menu a{display:block;padding:10px 18px;}
		</style>' . "\n";
}


// ---------------------------------------------------------------------------
// 10. Register a custom block category for LumoKit blocks in the editor
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
