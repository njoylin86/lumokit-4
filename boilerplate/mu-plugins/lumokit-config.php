<?php
/**
 * Plugin Name: LumoKit Config (Must-Use)
 * Description: Automatically activates ACF Pro license on every LumoKit-built site. Place this in /wp-content/mu-plugins/ — must-use plugins are auto-loaded by WordPress, no activation needed.
 * Version: 1.0.0
 * Author: LumoKit
 *
 * This file is part of the LumoKit boilerplate. It bakes in shared
 * configuration so a fresh WP install activates licensed plugins
 * (currently: ACF Pro) without manual key entry.
 */

defined( 'ABSPATH' ) || exit;

// ACF Pro license — read from a constant so the key isn't stored in the database
// and migrates with the codebase, not the WP database export.
if ( ! defined( 'ACF_PRO_LICENSE' ) ) {
	define( 'ACF_PRO_LICENSE', 'ZDRiNWMxMjU3YzZkMmMzZjFhMTc2ZGUyY2ExN2YxNWEyZGYzYjFlOWFjMDBhOTIwM2M0NzU2' );
}
