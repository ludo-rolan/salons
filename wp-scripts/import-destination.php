<?php
const PROJECT_NAME = 'aftg';
require 'init.php';

$regions_file = DATA_DIR . 'regions_full.json';
$countries_file = DATA_DIR . 'countries_full.json';
$destinations_dir = DATA_DIR . 'destinations/';

$regions = Scripts_Utils::read_json_file($regions_file);
$countries = Scripts_Utils::read_json_file($countries_file);

// run through all regions and create each as top level "destinations" taxonomy term
foreach ($regions as $region) {
	$region_name = $region['label'];
	$region_slug =
		($region["travelGuide"]["isTravelGuideAvailable"])
			?str_replace(
				'https://www.airfrance.fr/guide-voyage/',
				'',
				$region["travelGuide"]["travelGuideUrl"]
		)
			:Scripts_Utils::slugify( $region_name )
	;
	$region_term = wp_insert_term( $region_name, 'destinations', array( 'slug' => $region_slug ) );
	if ( is_wp_error( $region_term ) ) {
		echo "Error creating Destination (Region): $region_name\n";
		continue;
	}
	$region_id = $region_term['term_id'];
	echo "Created Destination: $region_name\n";
	// add meta data to the term
	$metas = array(
		"code",
		"pictureUrl",
		"latitude",
		"longitude",
	);
	foreach ($metas as $meta) {
		update_term_meta( $region_id, $meta, $region[$meta] );
	}
	update_term_meta( $region_id, "isTravelGuideAvailable", $region["travelGuide"]["isTravelGuideAvailable"] );
	update_term_meta( $region_id, "travelGuideUrl", $region["travelGuide"]["travelGuideUrl"] );

	// run through all countries in this region and create each as a child of the region
	foreach ( $region['countries'] as $country ) {
		$country = $countries[$country];
		$country_name = $country['label'];
		$country_slug = ($region["travelGuide"]["isTravelGuideAvailable"])
			?str_replace(
				'https://www.airfrance.fr/guide-voyage/',
				'',
				$region["travelGuide"]["travelGuideUrl"]
			)
			:Scripts_Utils::slugify( $region_name )
		;
		$country_term = wp_insert_term( $country_name, 'destinations', array(
			'slug'   => $country_slug,
			'parent' => $region_id
		));
		if ( is_wp_error( $country_term ) ) {
			echo "Error creating Country: $country_name\n";
			continue;
		}
		$country_id = $country_term['term_id'];
		$metas = array(
			"code",
			"pictureUrl",
			"latitude",
			"longitude",
		);
		foreach ($metas as $meta) {
			update_term_meta( $country_id, $meta, $country[$meta] );
		}
		update_term_meta( $country_id, "isTravelGuideAvailable", $country["travelGuide"]["isTravelGuideAvailable"] );
		update_term_meta( $country_id, "travelGuideUrl", $country["travelGuide"]["travelGuideUrl"] );
		echo "Created Destination (Country): $country_name\n";

		// run through all destinations in this country and create each as a child of the country
//		foreach ( $country['destinations'] as $destination ) {
//			$destination_name = $destination['name'];
//			$destination_slug = Scripts_Utils::slugify( $destination_name );
//			$destination_term = wp_insert_term( $destination_name, 'destinations', array(
//				'slug'   => $destination_slug,
//				'parent' => $country_id
//			) );
//			if ( is_wp_error( $destination_term ) ) {
//				echo "Error creating term: $destination_name\n";
//				continue;
//			}
//			$destination_id = $destination_term;
//	        echo "Created term: $destination_name\n";
//	    }
	}
}