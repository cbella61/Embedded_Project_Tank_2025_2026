"""Generatore Autodesk Fusion per il modello del carro armato.

Il file parameters.json deve contenere esclusivamente quote confermate.
Lo script interrompe la generazione se manca una quota obbligatoria, evitando
che una misura venga scelta arbitrariamente.
"""

import json
import math
import os
import traceback

import adsk.core
import adsk.fusion


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CAD_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
PARAMETERS_FILE = os.path.join(SCRIPT_DIR, "parameters.json")
EXCHANGE_DIR = os.path.join(CAD_DIR, "exchange")


REQUIRED_LOWER_BLANK_VALUES = (
    "chassis.lower_deck.length",
    "chassis.lower_deck.width",
    "chassis.lower_deck.thickness",
)


REQUIRED_TWO_DECK_BLANK_VALUES = REQUIRED_LOWER_BLANK_VALUES + (
    "chassis.upper_deck.length",
    "chassis.upper_deck.width",
    "chassis.upper_deck.thickness",
    "chassis.upper_deck.clearance_above_lower",
)


REQUIRED_STANDOFF_VALUES = REQUIRED_TWO_DECK_BLANK_VALUES + (
    "base_standoffs.outer_diameter",
    "base_standoffs.screw_hole_diameter",
    "base_standoffs.edge_inset",
    "base_standoffs.nut_across_flats",
    "base_standoffs.nut_trap_depth",
)


REQUIRED_ZIP_SLOT_VALUES = REQUIRED_STANDOFF_VALUES + (
    "chassis_mounting.slot_dimensions.length",
    "chassis_mounting.slot_dimensions.width",
)


REQUIRED_UPPER_ACCESS_VALUES = REQUIRED_ZIP_SLOT_VALUES + (
    "cable_holes.lower_service_hole.width",
    "cable_holes.lower_service_hole.length",
    "cable_holes.lower_service_hole.center_x",
    "cable_holes.lower_service_hole.north_from_south_edge",
    "cable_holes.lower_service_hole.center_y",
    "electronics.arduino.access_openings.width",
    "electronics.arduino.access_openings.length",
    "electronics.arduino.access_openings.center_x",
    "electronics.arduino.access_openings.center_y",
    "electronics.cannon_pcb_separate_battery_pack.opening_width",
    "electronics.cannon_pcb_separate_battery_pack.opening_length",
    "electronics.cannon_pcb_separate_battery_pack.opening_center_x",
    "electronics.cannon_pcb_separate_battery_pack.opening_center_y",
)


# Quote necessarie per creare i due piani completi di passacavi. Le altre parti
# vengono abilitate solo dopo aver confermato le rispettive dimensioni.
REQUIRED_BASE_VALUES = REQUIRED_TWO_DECK_BLANK_VALUES + (
    "cable_holes.motor_hole.diameter",
    "cable_holes.motor_hole.center_x",
    "cable_holes.motor_hole.center_y",
    "cable_holes.turret_hole.diameter",
    "cable_holes.turret_hole.center_x",
    "cable_holes.turret_hole.center_y",
)


REQUIRED_BATTERY_HOLDER_COMMON_VALUES = (
    "electronics.battery_holder.confirmed_dimensions.inner_length",
    "electronics.battery_holder.confirmed_dimensions.inner_width",
    "electronics.battery_holder.confirmed_dimensions.outer_length",
    "electronics.battery_holder.confirmed_dimensions.outer_width",
    "electronics.battery_holder.confirmed_dimensions.side_wall_thickness",
    "electronics.battery_holder.confirmed_dimensions.wall_height",
    "electronics.battery_holder.cable_exit.opening_length",
    "electronics.battery_holder.cable_exit.kind",
    "electronics.battery_holder.cable_exit.long_wall_side",
    "electronics.battery_holder.cable_exit.opening_end",
)


REQUIRED_BATTERY_HOLDER_VALUES = REQUIRED_BATTERY_HOLDER_COMMON_VALUES + (
    "electronics.battery_holder.confirmed_dimensions.bottom_thickness",
)


REQUIRED_HULL_SHELL_VALUES = (
    "hull_shell.inner_width",
    "hull_shell.inner_length",
    "hull_shell.outer_width",
    "hull_shell.outer_length",
    "hull_shell.clearance_per_side",
    "hull_shell.wall_thickness",
    "hull_shell.lower_skirt_height",
    "hull_shell.split_z",
    "hull_shell.continuous_side_wall_height",
    "hull_shell.top_lid_bottom_z",
    "hull_shell.ventilation_grilles.slot_count_per_wall",
    "hull_shell.ventilation_grilles.slot_width",
    "hull_shell.ventilation_grilles.slot_height",
    "hull_shell.ventilation_grilles.vertical_pitch",
    "hull_shell.ventilation_grilles.center_x",
    "hull_shell.ventilation_grilles.center_z",
    "hull_shell.mounting_tabs.upper_deck_clearance_hole_diameter",
    "hull_shell.mounting_tabs.printed_pilot_hole_diameter",
    "hull_shell.mounting_tabs.vertical_thickness",
    "hull_shell.mounting_tabs.span_parallel_to_wall",
    "hull_shell.mounting_tabs.depth_from_wall",
)


REQUIRED_COVER_TURRET_VALUES = (
    "electronics_cover.outer_length",
    "electronics_cover.outer_width",
    "electronics_cover.wall_height",
    "electronics_cover.roof_thickness",
    "electronics_cover.mounting_hole_diameter",
    "electronics_cover.mounting_hole_center_x",
    "electronics_cover.mounting_hole_center_y",
    "electronics_cover.central_roof_support.channel_floor_inner_radius",
    "electronics_cover.central_roof_support.channel_floor_outer_radius",
    "electronics_cover.central_roof_support.channel_floor_bottom_z",
    "electronics_cover.central_roof_support.channel_floor_thickness",
    "electronics_cover.central_roof_support.channel_wall_thickness",
    "electronics_cover.central_roof_support.channel_clearance_height",
    "base_standoffs.outer_diameter",
    "turret.stepper.body_diameter",
    "turret.stepper.body_height",
    "turret.stepper.shaft_diameter",
    "turret.stepper.shaft_flat_to_flat",
    "turret.stepper.shaft_length",
    "turret.stepper.mounting_hole_spacing",
    "turret.stepper.mounting_hole_diameter",
    "turret.stepper.mounting_countersink_diameter",
    "turret.stepper.mounting_countersink_depth",
    "turret.stepper.overall_tab_width",
    "turret.rotating_base.diameter",
    "turret.rotating_base.thickness",
    "turret.rotating_base.shaft_fit_clearance_per_side",
    "turret.rotating_base.shaft_bore_diameter",
    "turret.rotating_base.shaft_bore_flat_to_flat",
    "turret.rotating_base.coupling_hub_outer_diameter",
    "turret.rotating_base.coupling_hub_height_below_base",
    "turret.rotating_base.coupling_hub_roof_clearance_per_side",
    "turret.rotating_base.minimum_shaft_engagement",
    "turret.rotating_base.mounting_radius",
    "turret.rotating_base.mounting_hole_diameter",
    "turret.rotating_base.nut_across_flats",
    "turret.rotating_base.nut_trap_depth",
    "turret.azimuth_support.thrust_washer_inner_diameter",
    "turret.azimuth_support.thrust_washer_outer_diameter",
    "turret.azimuth_support.thrust_washer_thickness",
    "turret.azimuth_support.thrust_washer_seat_depth",
    "turret.azimuth_support.thrust_washer_seat_radial_clearance_per_side",
    "turret.azimuth_support.fixed_guide_inner_radius",
    "turret.azimuth_support.fixed_guide_outer_radius",
    "turret.azimuth_support.fixed_guide_height",
    "turret.azimuth_support.minimum_guide_engagement_at_full_lift",
    "turret.azimuth_support.rotating_groove_radial_clearance_per_side",
    "turret.azimuth_support.rotating_groove_depth",
    "turret.azimuth_support.anti_lift_clip_count",
    "turret.azimuth_support.anti_lift_vertical_clearance",
    "turret.azimuth_support.anti_lift_overlap",
    "turret.azimuth_support.anti_lift_foot_inner_radius",
    "turret.azimuth_support.anti_lift_foot_outer_radius",
    "turret.azimuth_support.anti_lift_tangential_width",
    "turret.azimuth_support.anti_lift_foot_thickness",
    "turret.azimuth_support.anti_lift_post_inner_radius",
    "turret.azimuth_support.anti_lift_post_outer_radius",
    "turret.azimuth_support.anti_lift_cap_outer_radius",
    "turret.azimuth_support.anti_lift_cap_thickness",
    "turret.azimuth_support.anti_lift_screw_radius",
    "turret.azimuth_support.anti_lift_screw_hole_diameter",
    "turret.azimuth_support.anti_lift_nut_across_flats",
    "turret.azimuth_support.anti_lift_nut_trap_depth",
    "turret.azimuth_support.anti_lift_key_height",
    "turret.azimuth_support.anti_lift_key_width",
    "turret.azimuth_support.anti_lift_key_side_clearance",
    "turret.azimuth_support.upper_frame_standoff_height",
    "turret.azimuth_support.upper_frame_standoff_diameter",
    "turret.azimuth_support.minimum_frame_to_clip_dynamic_clearance",
    "turret.elevation_frame.length",
    "turret.elevation_frame.width",
    "turret.elevation_frame.base_thickness",
    "turret.elevation_frame.height",
    "turret.elevation_frame.wall_thickness",
    "turret.elevation_frame.pivot_above_base_top",
    "turret.elevation_frame.mobile_side_clearance",
    "turret.elevation_frame.mobile_length",
    "turret.elevation_frame.mobile_plate_thickness",
    "turret.elevation_frame.mobile_ear_length",
    "turret.elevation_frame.mobile_ear_height",
    "turret.servo.body_length",
    "turret.servo.body_width",
    "turret.servo.body_height",
    "turret.servo.overall_height_with_output",
    "turret.servo.mounting_flange_overall_length",
    "turret.servo.mounting_ear_projection_nominal",
    "turret.servo.mounting_ear_thickness",
    "turret.servo.mounting_ear_hole_diameter",
    "turret.servo.mounting_ear_free_edge_ligament",
    "turret.servo.mounting_wall_slot_length",
    "turret.servo.mounting_wall_slot_width",
    "turret.servo.mounting_wall_min_web",
    "turret.servo.shaft_center_from_rear_body_end",
    "turret.servo.shaft_protrusion",
    "turret.servo.drive_shaft_diameter",
    "turret.servo.horn_reference_span",
    "turret.servo.horn_reference_arm_width",
    "turret.servo.horn_reference_thickness",
    "turret.servo.horn_reference_hub_diameter",
    "turret.servo.horn_adapter_disc_diameter",
    "turret.servo.horn_adapter_disc_thickness",
    "turret.servo.horn_adapter_center_access_diameter",
    "turret.servo.horn_adapter_outer_face_abs_x",
    "turret.servo.horn_adapter_adjustment_slot_length",
    "turret.servo.horn_adapter_adjustment_slot_width",
    "turret.servo.horn_adapter_shelf_thickness",
    "turret.servo.horn_adapter_shelf_inner_x_abs",
    "turret.servo.horn_adapter_shelf_length_y",
    "turret.servo.horn_adapter_fastener_center_y",
    "turret.servo.horn_adapter_tray_pilot_diameter",
    "turret.servo.horn_adapter_tray_pilot_depth",
    "turret.servo.fit_clearance_per_side",
    "turret.servo.holder_wall_thickness",
    "turret.servo.holder_shelf_thickness",
    "turret.servo.carter_screw_clearance_hole_diameter",
    "turret.servo.carter_screw_pilot_hole_diameter",
    "turret.cable_routing.servo_cable_profile_width",
    "turret.cable_routing.servo_cable_profile_thickness",
    "turret.cable_routing.routing_clearance_per_side",
    "turret.cable_routing.servo_holder_exit_notch_width",
    "turret.cable_routing.servo_holder_exit_notch_depth",
    "turret.cable_routing.servo_connector_width",
    "turret.cable_routing.servo_connector_thickness",
    "turret.cable_routing.common_connector_passage_width",
    "turret.cable_routing.common_connector_passage_length",
    "turret.cable_routing.cannon_connector_width",
    "turret.cable_routing.cannon_connector_thickness",
    "turret.cable_routing.cannon_mobile_passage_width",
    "turret.cable_routing.cannon_mobile_passage_length",
    "turret.cable_routing.rotating_passage_center_angle_deg",
    "turret.cable_routing.azimuth_arc_mean_radius",
    "turret.cable_routing.azimuth_arc_radial_width",
    "turret.cable_routing.azimuth_arc_start_deg",
    "turret.cable_routing.azimuth_arc_sweep_deg",
    "turret.cable_routing.azimuth_rotation_range_deg",
    "turret.cable_routing.azimuth_free_bundle_length",
    "turret.cable_routing.cable_tie_slot_length",
    "turret.cable_routing.cable_tie_slot_width",
    "turret.cable_routing.cable_tie_pair_spacing",
    "turret.cable_routing.mobile_cable_tie_pair_spacing",
    "turret.cable_routing.fixed_lower_anchor_pad_width",
    "turret.cable_routing.fixed_lower_anchor_pad_length",
    "turret.cable_routing.fixed_lower_anchor_pad_thickness",
    "turret.cable_routing.fixed_lower_anchor_pad_center_x",
    "turret.cable_routing.fixed_lower_anchor_pad_center_y",
    "turret.cable_routing.fixed_lower_anchor_slot_offset_x",
    "turret.cable_routing.fixed_lower_anchor_min_ligament",
    "turret.cable_routing.fixed_lower_anchor_bridge_width",
    "turret.cable_routing.fixed_lower_anchor_bridge_length",
    "turret.cable_routing.fixed_lower_anchor_bridge_center_x",
    "turret.cable_routing.fixed_lower_anchor_bridge_center_y",
    "turret.firing_module.pcb_length",
    "turret.firing_module.pcb_width",
    "turret.firing_module.pcb_thickness",
    "turret.firing_module.mounting_hole_diameter",
    "turret.firing_module.mounting_hole_edge_inset_x",
    "turret.firing_module.mounting_hole_edge_inset_y",
    "turret.firing_module.barrel_protrusion_from_cannon_outlet",
    "turret.firing_module.barrel_outer_diameter",
    "turret.firing_module.barrel_wall_thickness",
    "turret.firing_module.barrel_inner_diameter",
    "turret.firing_module.cannon_outer_diameter_at_solenoid",
    "turret.firing_module.solenoid_length",
    "turret.firing_module.overall_height_from_pcb_bottom",
    "turret.manual_loader.provisional_max_projectile_diameter",
    "turret.manual_loader.provisional_max_projectile_length",
    "turret.manual_loader.projectile_radial_clearance",
    "turret.manual_loader.guide_outer_diameter",
    "turret.manual_loader.guide_inner_diameter",
    "turret.manual_loader.guide_length",
    "turret.manual_loader.guide_to_solenoid_clearance",
    "turret.manual_loader.guide_roof_rib_width",
    "turret.manual_loader.guide_roof_rib_overlap",
    "turret.manual_loader.rear_window_width",
    "turret.manual_loader.rear_window_bottom_above_shroud_bottom",
    "turret.manual_loader.roof_slot_length",
    "turret.manual_loader.hatch_top_pocket_width",
    "turret.manual_loader.hatch_top_pocket_length",
    "turret.manual_loader.hatch_top_pocket_depth",
    "turret.manual_loader.hatch_top_plate_thickness",
    "turret.manual_loader.hatch_vertical_clearance",
    "turret.manual_loader.hatch_vertical_plate_thickness",
    "turret.manual_loader.hatch_clearance_per_side",
    "turret.manual_loader.hatch_local_reinforcement_thickness",
    "turret.manual_loader.hatch_local_reinforcement_length",
    "turret.manual_loader.mounting_hole_spacing",
    "turret.manual_loader.mounting_hole_center_from_rear_edge",
    "turret.manual_loader.clearance_hole_diameter",
    "turret.manual_loader.pilot_hole_diameter",
    "turret.manual_loader.screw_boss_diameter",
    "turret.manual_loader.screw_boss_height",
    "turret.manual_loader.countersink_diameter",
    "turret.manual_loader.countersink_depth",
    "turret.manual_loader.minimum_printed_wall",
)


REQUIRED_FULL_REFERENCE_ASSEMBLY_VALUES = (
    REQUIRED_UPPER_ACCESS_VALUES
    + REQUIRED_BATTERY_HOLDER_COMMON_VALUES
    + REQUIRED_HULL_SHELL_VALUES
    + REQUIRED_COVER_TURRET_VALUES
    + (
        "electronics.arduino.length",
        "electronics.arduino.width",
        "electronics.arduino.board_thickness",
        "electronics.arduino.mounting_hole_diameter",
        "electronics.lower_deck_layout.battery_holder.center_x",
        "electronics.lower_deck_layout.battery_holder.center_y",
        "electronics.lower_deck_layout.arduino_and_shield.center_x",
        "electronics.lower_deck_layout.arduino_and_shield.center_y",
        "electronics.lower_deck_layout.arduino_and_shield.rotation_deg_counterclockwise",
    )
)


def _read_parameters():
    with open(PARAMETERS_FILE, "r", encoding="utf-8") as stream:
        return json.load(stream)


def _get(data, dotted_path):
    value = data
    for key in dotted_path.split("."):
        value = value[key]
    return value


def _missing_values(data, paths):
    missing = []
    for path in paths:
        try:
            value = _get(data, path)
        except (KeyError, TypeError):
            missing.append(path)
            continue
        if value is None or value == "":
            missing.append(path)
    return missing


def _validate_positive(data, paths):
    invalid = []
    for path in paths:
        value = _get(data, path)
        if not isinstance(value, (int, float)) or value <= 0:
            invalid.append(path)
    return invalid


def _validate_upper_access_openings(upper, standoffs, openings):
    """Controlla bordi, sovrapposizioni e interferenze con le colonnine."""
    deck_half_width = upper["width"] / 2.0
    deck_half_length = upper["length"] / 2.0
    bounds = []

    for opening in openings:
        half_width = opening["width"] / 2.0
        half_length = opening["length"] / 2.0
        minimum_x = opening["center_x"] - half_width
        maximum_x = opening["center_x"] + half_width
        minimum_y = opening["center_y"] - half_length
        maximum_y = opening["center_y"] + half_length
        if (
            minimum_x <= -deck_half_width
            or maximum_x >= deck_half_width
            or minimum_y <= -deck_half_length
            or maximum_y >= deck_half_length
        ):
            raise RuntimeError(
                f"L'apertura {opening['name']} deve rimanere completamente "
                "all'interno del piano superiore."
            )
        bounds.append(
            {
                "name": opening["name"],
                "minimum_x": minimum_x,
                "maximum_x": maximum_x,
                "minimum_y": minimum_y,
                "maximum_y": maximum_y,
            }
        )

    first, second = bounds
    rectangles_overlap = (
        first["minimum_x"] < second["maximum_x"]
        and first["maximum_x"] > second["minimum_x"]
        and first["minimum_y"] < second["maximum_y"]
        and first["maximum_y"] > second["minimum_y"]
    )
    if rectangles_overlap:
        raise RuntimeError(
            "Le aperture superiori Arduino e pacco batteria non devono "
            "sovrapporsi."
        )

    inset = standoffs["edge_inset"]
    standoff_radius = standoffs["outer_diameter"] / 2.0
    standoff_x = upper["width"] / 2.0 - inset
    standoff_y = upper["length"] / 2.0 - inset
    standoff_centers = (
        (-standoff_x, -standoff_y),
        (standoff_x, -standoff_y),
        (standoff_x, standoff_y),
        (-standoff_x, standoff_y),
    )
    for opening in bounds:
        for center_x, center_y in standoff_centers:
            closest_x = min(
                max(center_x, opening["minimum_x"]), opening["maximum_x"]
            )
            closest_y = min(
                max(center_y, opening["minimum_y"]), opening["maximum_y"]
            )
            delta_x = center_x - closest_x
            delta_y = center_y - closest_y
            if delta_x * delta_x + delta_y * delta_y <= standoff_radius ** 2:
                raise RuntimeError(
                    f"L'apertura {opening['name']} interferisce con una "
                    "colonnina principale."
                )


def _rectangle_bounds(name, width, length, center_x, center_y):
    return {
        "name": name,
        "minimum_x": center_x - width / 2.0,
        "maximum_x": center_x + width / 2.0,
        "minimum_y": center_y - length / 2.0,
        "maximum_y": center_y + length / 2.0,
    }


def _rectangles_overlap(first, second):
    return (
        first["minimum_x"] < second["maximum_x"]
        and first["maximum_x"] > second["minimum_x"]
        and first["minimum_y"] < second["maximum_y"]
        and first["maximum_y"] > second["minimum_y"]
    )


def _rectangle_circle_clearance(rectangle, center_x, center_y, radius):
    closest_x = min(
        max(center_x, rectangle["minimum_x"]), rectangle["maximum_x"]
    )
    closest_y = min(
        max(center_y, rectangle["minimum_y"]), rectangle["maximum_y"]
    )
    return math.sqrt((center_x - closest_x) ** 2 + (center_y - closest_y) ** 2) - radius


def _validate_lower_deck_layout(data):
    """Valida il layout XY confermato senza assumere quote verticali Arduino."""
    lower = data["chassis"]["lower_deck"]
    standoffs = data["base_standoffs"]
    mounting = data["chassis_mounting"]
    electronics = data["electronics"]
    holder_dims = electronics["battery_holder"]["confirmed_dimensions"]
    layout = electronics["lower_deck_layout"]
    holder_layout = layout["battery_holder"]
    arduino_layout = layout["arduino_and_shield"]
    arduino = electronics["arduino"]
    pack = electronics["cannon_pcb_separate_battery_pack"]
    service_hole = data["cable_holes"]["lower_service_hole"]

    rotation = arduino_layout["rotation_deg_counterclockwise"] % 360
    if abs(rotation - 90.0) > 1e-6:
        raise RuntimeError(
            "Il riferimento Arduino attuale supporta la rotazione confermata di 90 gradi."
        )

    holder_bounds = _rectangle_bounds(
        "supporto batteria",
        holder_dims["outer_width"],
        holder_dims["outer_length"],
        holder_layout["center_x"],
        holder_layout["center_y"],
    )
    arduino_bounds = _rectangle_bounds(
        "Arduino UNO R4 WiFi",
        arduino["width"],
        arduino["length"],
        arduino_layout["center_x"],
        arduino_layout["center_y"],
    )
    expected_service_y = (
        -lower["length"] / 2.0 + service_hole["north_from_south_edge"]
    )
    if abs(service_hole["center_y"] - expected_service_y) > 1e-6:
        raise RuntimeError(
            "Il centro Y del foro 10x10 deve corrispondere alla quota dal bordo Sud."
        )
    service_hole_bounds = _rectangle_bounds(
        "foro di servizio 10x10",
        service_hole["width"],
        service_hole["length"],
        service_hole["center_x"],
        service_hole["center_y"],
    )
    deck_half_width = lower["width"] / 2.0
    deck_half_length = lower["length"] / 2.0
    for footprint in (holder_bounds, arduino_bounds, service_hole_bounds):
        if (
            footprint["minimum_x"] < -deck_half_width
            or footprint["maximum_x"] > deck_half_width
            or footprint["minimum_y"] < -deck_half_length
            or footprint["maximum_y"] > deck_half_length
        ):
            raise RuntimeError(
                f"L'ingombro {footprint['name']} supera il piano inferiore."
            )

    if _rectangles_overlap(holder_bounds, arduino_bounds):
        raise RuntimeError("Supporto batteria e Arduino non devono sovrapporsi.")
    if _rectangles_overlap(service_hole_bounds, holder_bounds):
        raise RuntimeError("Il foro 10x10 non deve intersecare il supporto batteria.")
    if _rectangles_overlap(service_hole_bounds, arduino_bounds):
        raise RuntimeError("Il foro 10x10 non deve essere coperto dall'Arduino.")

    inset = standoffs["edge_inset"]
    standoff_x = lower["width"] / 2.0 - inset
    standoff_y = lower["length"] / 2.0 - inset
    standoff_centers = (
        (-standoff_x, -standoff_y),
        (standoff_x, -standoff_y),
        (standoff_x, standoff_y),
        (-standoff_x, standoff_y),
    )
    minimum_print_clearance = 2.0
    for footprint in (holder_bounds, arduino_bounds, service_hole_bounds):
        for center_x, center_y in standoff_centers:
            clearance = _rectangle_circle_clearance(
                footprint,
                center_x,
                center_y,
                standoffs["outer_diameter"] / 2.0,
            )
            if clearance < minimum_print_clearance:
                raise RuntimeError(
                    f"L'ingombro {footprint['name']} deve lasciare almeno "
                    f"{minimum_print_clearance} mm da ogni colonnina."
                )

    slot_dimensions = mounting["slot_dimensions"]
    for index, slot in enumerate(mounting["slot_positions"], start=1):
        slot_bounds = _rectangle_bounds(
            f"asola fascetta {index}",
            slot_dimensions["length"],
            slot_dimensions["width"],
            slot["east_west"],
            -lower["length"] / 2.0 + slot["north_from_south_edge"],
        )
        if _rectangles_overlap(holder_bounds, slot_bounds):
            raise RuntimeError(
                f"Il supporto batteria copre l'asola fascetta {index}."
            )
        if _rectangles_overlap(service_hole_bounds, slot_bounds):
            raise RuntimeError(
                f"Il foro 10x10 interseca l'asola fascetta {index}."
            )

    horizontal_gap_to_arduino = (
        arduino_bounds["minimum_x"] - service_hole_bounds["maximum_x"]
    )
    if horizontal_gap_to_arduino < minimum_print_clearance:
        raise RuntimeError(
            "Il foro 10x10 deve lasciare almeno 2 mm dal lato Ovest dell'Arduino."
        )

    if (
        abs(pack["opening_center_x"] - holder_layout["center_x"]) > 1e-6
        or abs(pack["opening_center_y"] - holder_layout["center_y"]) > 1e-6
        or pack["opening_width"] > holder_dims["inner_width"]
        or pack["opening_length"] > holder_dims["inner_length"]
    ):
        raise RuntimeError(
            "Il passaggio del pacco batteria PCB deve restare centrato e "
            "contenuto nel vano del supporto batteria."
        )


def _validate_hull_shell(data):
    """Valida il guscio removibile rispetto ai due piani confermati."""
    lower = data["chassis"]["lower_deck"]
    upper = data["chassis"]["upper_deck"]
    shell = data["hull_shell"]
    cover = data["electronics_cover"]
    mounting_tabs = shell["mounting_tabs"]
    ventilation = shell["ventilation_grilles"]

    expected_inner_width = lower["width"] + 2.0 * shell["clearance_per_side"]
    expected_inner_length = lower["length"] + 2.0 * shell["clearance_per_side"]
    expected_outer_width = expected_inner_width + 2.0 * shell["wall_thickness"]
    expected_outer_length = expected_inner_length + 2.0 * shell["wall_thickness"]
    expected_split_z = (
        lower["thickness"]
        + upper["clearance_above_lower"]
        + upper["thickness"]
    )
    expected_top_lid_z = expected_split_z + cover["wall_height"]

    checks = (
        (shell["inner_width"], expected_inner_width, "larghezza interna"),
        (shell["inner_length"], expected_inner_length, "lunghezza interna"),
        (shell["outer_width"], expected_outer_width, "larghezza esterna"),
        (shell["outer_length"], expected_outer_length, "lunghezza esterna"),
        (shell["lower_skirt_height"], expected_split_z, "altezza guscio inferiore"),
        (shell["split_z"], expected_split_z, "quota di separazione"),
        (
            shell["continuous_side_wall_height"],
            expected_top_lid_z,
            "altezza parete laterale continua",
        ),
        (shell["top_lid_bottom_z"], expected_top_lid_z, "quota coperchio superiore"),
        (cover["outer_width"], shell["outer_width"], "raccordo larghezza coperchio"),
        (cover["outer_length"], shell["outer_length"], "raccordo lunghezza coperchio"),
    )
    for actual, expected, label in checks:
        if abs(actual - expected) > 1e-6:
            raise RuntimeError(
                f"Guscio carro incoerente ({label}): {actual} mm invece di {expected} mm."
            )

    slot_count = ventilation["slot_count_per_wall"]
    if not isinstance(slot_count, int) or slot_count < 1:
        raise RuntimeError("La griglia deve contenere almeno una feritoia per parete.")
    grille_bottom = (
        ventilation["center_z"]
        - (slot_count - 1) * ventilation["vertical_pitch"] / 2.0
        - ventilation["slot_height"] / 2.0
    )
    grille_top = (
        ventilation["center_z"]
        + (slot_count - 1) * ventilation["vertical_pitch"] / 2.0
        + ventilation["slot_height"] / 2.0
    )
    if grille_bottom <= lower["thickness"] + 2.0 or grille_top >= shell["split_z"] - 2.0:
        raise RuntimeError(
            "Le griglie del vano inferiore devono lasciare almeno 2 mm dai due piani."
        )
    if (
        abs(ventilation["center_x"]) + ventilation["slot_width"] / 2.0
        >= shell["inner_width"] / 2.0 - 2.0
    ):
        raise RuntimeError("Le griglie devono lasciare almeno 2 mm dai bordi laterali.")
    if ventilation["vertical_pitch"] <= ventilation["slot_height"]:
        raise RuntimeError("Fra le feritoie deve rimanere un legamento stampabile.")

    boss_radius = data["base_standoffs"]["outer_diameter"] / 2.0
    if (
        abs(cover["mounting_hole_center_x"]) + boss_radius
        >= shell["inner_width"] / 2.0
        or abs(cover["mounting_hole_center_y"]) + boss_radius
        >= shell["inner_length"] / 2.0
    ):
        raise RuntimeError(
            "I boss M3 del tetto devono poter entrare verticalmente nel guscio continuo."
        )

    tab_positions = mounting_tabs.get("positions", [])
    if len(tab_positions) != 4:
        raise RuntimeError("Il guscio inferiore richiede esattamente quattro linguette M2.5.")
    valid_walls = {"south", "north", "east", "west"}
    for tab in tab_positions:
        if tab.get("wall") not in valid_walls:
            raise RuntimeError("Ogni linguetta del guscio deve indicare una parete valida.")
        center_x = tab.get("x")
        center_y = tab.get("y")
        if not isinstance(center_x, (int, float)) or not isinstance(
            center_y, (int, float)
        ):
            raise RuntimeError("Le coordinate delle linguette M2.5 devono essere numeriche.")
        edge_margin = mounting_tabs["upper_deck_clearance_hole_diameter"] / 2.0
        if abs(center_x) + edge_margin >= upper["width"] / 2.0 or abs(
            center_y
        ) + edge_margin >= upper["length"] / 2.0:
            raise RuntimeError("Una linguetta M2.5 esce dal piano superiore.")


def _mm_to_cm(value_mm):
    """Fusion usa centimetri come unità interne per le lunghezze."""
    return float(value_mm) / 10.0


def _value_mm(value_mm):
    return adsk.core.ValueInput.createByString(f"{float(value_mm)} mm")


def _add_user_parameter(design, name, value, units, comment):
    parameters = design.userParameters
    existing = parameters.itemByName(name)
    expression = f"{float(value)} {units}" if units else str(float(value))
    if existing:
        existing.expression = expression
        existing.comment = comment
        return existing
    return parameters.add(
        name,
        adsk.core.ValueInput.createByString(expression),
        units,
        comment,
    )


def _new_component(root_component, name):
    occurrence = root_component.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    component = occurrence.component
    component.name = name
    return component


def _offset_plane(component, offset_expression):
    if offset_expression in ("0", "0 mm"):
        return component.xYConstructionPlane
    plane_input = component.constructionPlanes.createInput()
    plane_input.setByOffset(
        component.xYConstructionPlane,
        adsk.core.ValueInput.createByString(offset_expression),
    )
    return component.constructionPlanes.add(plane_input)


def _centered_rectangle_prism(
    component,
    body_name,
    width_mm,
    length_mm,
    thickness_expression,
    z_expression="0 mm",
):
    plane = _offset_plane(component, z_expression)
    sketch = component.sketches.add(plane)
    sketch.name = f"Schizzo_{body_name}"

    half_width = _mm_to_cm(width_mm) / 2.0
    half_length = _mm_to_cm(length_mm) / 2.0
    sketch.sketchCurves.sketchLines.addTwoPointRectangle(
        adsk.core.Point3D.create(-half_width, -half_length, 0),
        adsk.core.Point3D.create(half_width, half_length, 0),
    )

    if sketch.profiles.count != 1:
        raise RuntimeError(f"Profilo rettangolare non valido per {body_name}")

    extrudes = component.features.extrudeFeatures
    extrude_input = extrudes.createInput(
        sketch.profiles.item(0),
        adsk.fusion.FeatureOperations.NewBodyFeatureOperation,
    )
    extent = adsk.fusion.DistanceExtentDefinition.create(
        adsk.core.ValueInput.createByString(thickness_expression)
    )
    extrude_input.setOneSideExtent(
        extent,
        adsk.fusion.ExtentDirections.PositiveExtentDirection,
    )
    feature = extrudes.add(extrude_input)
    feature.name = f"Estrusione_{body_name}"
    feature.bodies.item(0).name = body_name
    return feature.bodies.item(0), plane


def _rectangle_prism_at(
    component,
    plane,
    body_name,
    width_mm,
    length_mm,
    center_x_mm,
    center_y_mm,
    height_expression,
    operation=adsk.fusion.FeatureOperations.NewBodyFeatureOperation,
):
    sketch = component.sketches.add(plane)
    sketch.name = f"Schizzo_{body_name}"
    half_width = _mm_to_cm(width_mm) / 2.0
    half_length = _mm_to_cm(length_mm) / 2.0
    center_x = _mm_to_cm(center_x_mm)
    center_y = _mm_to_cm(center_y_mm)
    sketch.sketchCurves.sketchLines.addTwoPointRectangle(
        adsk.core.Point3D.create(
            center_x - half_width,
            center_y - half_length,
            0,
        ),
        adsk.core.Point3D.create(
            center_x + half_width,
            center_y + half_length,
            0,
        ),
    )
    if sketch.profiles.count != 1:
        raise RuntimeError(f"Profilo rettangolare non valido per {body_name}")

    extrudes = component.features.extrudeFeatures
    extrude_input = extrudes.createInput(sketch.profiles.item(0), operation)
    extent = adsk.fusion.DistanceExtentDefinition.create(
        adsk.core.ValueInput.createByString(height_expression)
    )
    extrude_input.setOneSideExtent(
        extent,
        adsk.fusion.ExtentDirections.PositiveExtentDirection,
    )
    feature = extrudes.add(extrude_input)
    feature.name = f"Estrusione_{body_name}"
    if operation == adsk.fusion.FeatureOperations.NewBodyFeatureOperation:
        feature.bodies.item(0).name = body_name
    return feature.bodies.item(0)


def _cut_rectangle(
    component,
    plane,
    width_mm,
    length_mm,
    center_x_mm,
    center_y_mm,
    cut_depth_expression,
    cut_name,
):
    sketch = component.sketches.add(plane)
    sketch.name = f"Schizzo_{cut_name}"
    half_width = _mm_to_cm(width_mm) / 2.0
    half_length = _mm_to_cm(length_mm) / 2.0
    center_x = _mm_to_cm(center_x_mm)
    center_y = _mm_to_cm(center_y_mm)
    sketch.sketchCurves.sketchLines.addTwoPointRectangle(
        adsk.core.Point3D.create(
            center_x - half_width,
            center_y - half_length,
            0,
        ),
        adsk.core.Point3D.create(
            center_x + half_width,
            center_y + half_length,
            0,
        ),
    )
    if sketch.profiles.count != 1:
        raise RuntimeError(f"Profilo rettangolare non valido per {cut_name}")

    extrudes = component.features.extrudeFeatures
    cut_input = extrudes.createInput(
        sketch.profiles.item(0),
        adsk.fusion.FeatureOperations.CutFeatureOperation,
    )
    extent = adsk.fusion.DistanceExtentDefinition.create(
        adsk.core.ValueInput.createByString(cut_depth_expression)
    )
    cut_input.setOneSideExtent(
        extent,
        adsk.fusion.ExtentDirections.PositiveExtentDirection,
    )
    feature = extrudes.add(cut_input)
    feature.name = cut_name
    return feature


def _cut_rotated_rectangle(
    component,
    plane,
    radial_width_mm,
    tangential_length_mm,
    center_radius_mm,
    center_angle_deg,
    cut_depth_expression,
    cut_name,
):
    """Taglia un rettangolo orientato radialmente rispetto all'origine."""
    sketch = component.sketches.add(plane)
    sketch.name = f"Schizzo_{cut_name}"
    angle = math.radians(center_angle_deg)
    radial = (math.cos(angle), math.sin(angle))
    tangent = (-math.sin(angle), math.cos(angle))
    center = (
        _mm_to_cm(center_radius_mm) * radial[0],
        _mm_to_cm(center_radius_mm) * radial[1],
    )
    half_radial = _mm_to_cm(radial_width_mm) / 2.0
    half_tangent = _mm_to_cm(tangential_length_mm) / 2.0
    points = []
    for radial_sign, tangent_sign in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
        points.append(
            adsk.core.Point3D.create(
                center[0]
                + radial_sign * half_radial * radial[0]
                + tangent_sign * half_tangent * tangent[0],
                center[1]
                + radial_sign * half_radial * radial[1]
                + tangent_sign * half_tangent * tangent[1],
                0,
            )
        )
    lines = sketch.sketchCurves.sketchLines
    for index in range(4):
        lines.addByTwoPoints(points[index], points[(index + 1) % 4])
    if sketch.profiles.count != 1:
        raise RuntimeError(f"Profilo rettangolare ruotato non valido per {cut_name}")
    extrudes = component.features.extrudeFeatures
    cut_input = extrudes.createInput(
        sketch.profiles.item(0),
        adsk.fusion.FeatureOperations.CutFeatureOperation,
    )
    extent = adsk.fusion.DistanceExtentDefinition.create(
        adsk.core.ValueInput.createByString(cut_depth_expression)
    )
    cut_input.setOneSideExtent(
        extent,
        adsk.fusion.ExtentDirections.PositiveExtentDirection,
    )
    feature = extrudes.add(cut_input)
    feature.name = cut_name
    return feature


def _cut_annular_sector(
    component,
    plane,
    mean_radius_mm,
    radial_width_mm,
    start_angle_deg,
    sweep_angle_deg,
    cut_depth_expression,
    cut_name,
):
    """Taglia un settore anulare usato come guida cavi di azimut."""
    inner_radius = mean_radius_mm - radial_width_mm / 2.0
    outer_radius = mean_radius_mm + radial_width_mm / 2.0
    if inner_radius <= 0 or sweep_angle_deg <= 0 or sweep_angle_deg >= 360:
        raise RuntimeError(f"Quote settore anulare non valide per {cut_name}")
    start = math.radians(start_angle_deg)
    sweep = math.radians(sweep_angle_deg)
    end = start + sweep
    center = adsk.core.Point3D.create(0, 0, 0)
    outer_start = adsk.core.Point3D.create(
        _mm_to_cm(outer_radius) * math.cos(start),
        _mm_to_cm(outer_radius) * math.sin(start),
        0,
    )
    outer_end = adsk.core.Point3D.create(
        _mm_to_cm(outer_radius) * math.cos(end),
        _mm_to_cm(outer_radius) * math.sin(end),
        0,
    )
    inner_start = adsk.core.Point3D.create(
        _mm_to_cm(inner_radius) * math.cos(start),
        _mm_to_cm(inner_radius) * math.sin(start),
        0,
    )
    inner_end = adsk.core.Point3D.create(
        _mm_to_cm(inner_radius) * math.cos(end),
        _mm_to_cm(inner_radius) * math.sin(end),
        0,
    )
    sketch = component.sketches.add(plane)
    sketch.name = f"Schizzo_{cut_name}"
    arcs = sketch.sketchCurves.sketchArcs
    arcs.addByCenterStartSweep(center, outer_start, sweep)
    arcs.addByCenterStartSweep(center, inner_end, -sweep)
    lines = sketch.sketchCurves.sketchLines
    lines.addByTwoPoints(outer_start, inner_start)
    lines.addByTwoPoints(outer_end, inner_end)
    if sketch.profiles.count != 1:
        raise RuntimeError(f"Profilo settore anulare non valido per {cut_name}")
    extrudes = component.features.extrudeFeatures
    cut_input = extrudes.createInput(
        sketch.profiles.item(0),
        adsk.fusion.FeatureOperations.CutFeatureOperation,
    )
    extent = adsk.fusion.DistanceExtentDefinition.create(
        adsk.core.ValueInput.createByString(cut_depth_expression)
    )
    cut_input.setOneSideExtent(
        extent,
        adsk.fusion.ExtentDirections.PositiveExtentDirection,
    )
    feature = extrudes.add(cut_input)
    feature.name = cut_name
    return feature


def _cut_annular_ring(
    component,
    plane,
    mean_radius_mm,
    radial_width_mm,
    cut_depth_expression,
    cut_name,
):
    """Taglia un anello completo per una corsa limitata da -180 a +180 gradi."""
    inner_radius = mean_radius_mm - radial_width_mm / 2.0
    outer_radius = mean_radius_mm + radial_width_mm / 2.0
    if inner_radius <= 0 or outer_radius <= inner_radius:
        raise RuntimeError(f"Quote anello non valide per {cut_name}")
    sketch = component.sketches.add(plane)
    sketch.name = f"Schizzo_{cut_name}"
    center = adsk.core.Point3D.create(0, 0, 0)
    circles = sketch.sketchCurves.sketchCircles
    circles.addByCenterRadius(center, _mm_to_cm(outer_radius))
    circles.addByCenterRadius(center, _mm_to_cm(inner_radius))

    ring_profile = None
    for index in range(sketch.profiles.count):
        candidate = sketch.profiles.item(index)
        if candidate.profileLoops.count == 2:
            ring_profile = candidate
            break
    if not ring_profile:
        raise RuntimeError(f"Profilo anulare non valido per {cut_name}")

    extrudes = component.features.extrudeFeatures
    cut_input = extrudes.createInput(
        ring_profile,
        adsk.fusion.FeatureOperations.CutFeatureOperation,
    )
    extent = adsk.fusion.DistanceExtentDefinition.create(
        adsk.core.ValueInput.createByString(cut_depth_expression)
    )
    cut_input.setOneSideExtent(
        extent,
        adsk.fusion.ExtentDirections.PositiveExtentDirection,
    )
    feature = extrudes.add(cut_input)
    feature.name = cut_name
    return feature


def _annular_prism(
    component,
    plane,
    body_name,
    inner_radius_mm,
    outer_radius_mm,
    height_expression,
    operation=adsk.fusion.FeatureOperations.NewBodyFeatureOperation,
):
    """Crea un prisma anulare, usato per il canale cavi senza ostacoli."""
    if inner_radius_mm <= 0 or outer_radius_mm <= inner_radius_mm:
        raise RuntimeError(f"Quote anello non valide per {body_name}")
    sketch = component.sketches.add(plane)
    sketch.name = f"Schizzo_{body_name}"
    center = adsk.core.Point3D.create(0, 0, 0)
    circles = sketch.sketchCurves.sketchCircles
    circles.addByCenterRadius(center, _mm_to_cm(outer_radius_mm))
    circles.addByCenterRadius(center, _mm_to_cm(inner_radius_mm))

    ring_profile = None
    for index in range(sketch.profiles.count):
        candidate = sketch.profiles.item(index)
        if candidate.profileLoops.count == 2:
            ring_profile = candidate
            break
    if not ring_profile:
        raise RuntimeError(f"Profilo anulare non valido per {body_name}")

    extrudes = component.features.extrudeFeatures
    extrude_input = extrudes.createInput(ring_profile, operation)
    extent = adsk.fusion.DistanceExtentDefinition.create(
        adsk.core.ValueInput.createByString(height_expression)
    )
    extrude_input.setOneSideExtent(
        extent,
        adsk.fusion.ExtentDirections.PositiveExtentDirection,
    )
    feature = extrudes.add(extrude_input)
    feature.name = f"Estrusione_{body_name}"
    if operation == adsk.fusion.FeatureOperations.NewBodyFeatureOperation:
        feature.bodies.item(0).name = body_name
    return feature


def _combine_join(component, target_body, tool_bodies, feature_name):
    """Unisce corpi già sovrapposti e fallisce esplicitamente se il join non riesce."""
    tools = adsk.core.ObjectCollection.create()
    for tool_body in tool_bodies:
        tools.add(tool_body)
    if tools.count == 0:
        raise RuntimeError(f"Nessun corpo utensile per {feature_name}")
    combine_features = component.features.combineFeatures
    combine_input = combine_features.createInput(target_body, tools)
    combine_input.operation = adsk.fusion.FeatureOperations.JoinFeatureOperation
    combine_input.isKeepToolBodies = False
    feature = combine_features.add(combine_input)
    if not feature:
        raise RuntimeError(f"Impossibile unire i corpi per {feature_name}")
    feature.name = feature_name
    return feature


def _cut_round_hole(
    component,
    plane,
    diameter_mm,
    center_x_mm,
    center_y_mm,
    cut_depth_expression,
    hole_name,
):
    sketch = component.sketches.add(plane)
    sketch.name = f"Schizzo_{hole_name}"
    sketch.sketchCurves.sketchCircles.addByCenterRadius(
        adsk.core.Point3D.create(
            _mm_to_cm(center_x_mm),
            _mm_to_cm(center_y_mm),
            0,
        ),
        _mm_to_cm(diameter_mm) / 2.0,
    )
    if sketch.profiles.count != 1:
        raise RuntimeError(f"Profilo circolare non valido per {hole_name}")

    extrudes = component.features.extrudeFeatures
    cut_input = extrudes.createInput(
        sketch.profiles.item(0),
        adsk.fusion.FeatureOperations.CutFeatureOperation,
    )
    extent = adsk.fusion.DistanceExtentDefinition.create(
        adsk.core.ValueInput.createByString(cut_depth_expression)
    )
    cut_input.setOneSideExtent(
        extent,
        adsk.fusion.ExtentDirections.PositiveExtentDirection,
    )
    cut_feature = extrudes.add(cut_input)
    cut_feature.name = hole_name
    return cut_feature


def _cut_countersink_frustum(
    component,
    lower_plane,
    upper_plane,
    lower_diameter_mm,
    upper_diameter_mm,
    center_x_mm,
    center_y_mm,
    feature_name,
):
    """Taglia una svasatura conica tra due cerchi su piani paralleli."""
    if lower_diameter_mm <= 0 or upper_diameter_mm <= lower_diameter_mm:
        raise RuntimeError(f"Diametri svasatura non validi per {feature_name}")

    section_profiles = []
    for label, plane, diameter in (
        ("inferiore", lower_plane, lower_diameter_mm),
        ("superiore", upper_plane, upper_diameter_mm),
    ):
        sketch = component.sketches.add(plane)
        sketch.name = f"Schizzo_{feature_name}_{label}"
        sketch.sketchCurves.sketchCircles.addByCenterRadius(
            adsk.core.Point3D.create(
                _mm_to_cm(center_x_mm),
                _mm_to_cm(center_y_mm),
                0,
            ),
            _mm_to_cm(diameter) / 2.0,
        )
        if sketch.profiles.count != 1:
            raise RuntimeError(f"Profilo svasatura non valido per {feature_name}")
        section_profiles.append(sketch.profiles.item(0))

    lofts = component.features.loftFeatures
    loft_input = lofts.createInput(adsk.fusion.FeatureOperations.CutFeatureOperation)
    for profile in section_profiles:
        loft_input.loftSections.add(profile)
    feature = lofts.add(loft_input)
    feature.name = feature_name
    return feature


def _cylinder_prism(
    component,
    plane,
    body_name,
    diameter_mm,
    center_x_mm,
    center_y_mm,
    height_expression,
    operation=adsk.fusion.FeatureOperations.NewBodyFeatureOperation,
):
    sketch = component.sketches.add(plane)
    sketch.name = f"Schizzo_{body_name}"
    sketch.sketchCurves.sketchCircles.addByCenterRadius(
        adsk.core.Point3D.create(
            _mm_to_cm(center_x_mm),
            _mm_to_cm(center_y_mm),
            0,
        ),
        _mm_to_cm(diameter_mm) / 2.0,
    )
    if sketch.profiles.count != 1:
        raise RuntimeError(f"Profilo circolare non valido per {body_name}")

    extrudes = component.features.extrudeFeatures
    extrude_input = extrudes.createInput(
        sketch.profiles.item(0),
        operation,
    )
    extent = adsk.fusion.DistanceExtentDefinition.create(
        adsk.core.ValueInput.createByString(height_expression)
    )
    extrude_input.setOneSideExtent(
        extent,
        adsk.fusion.ExtentDirections.PositiveExtentDirection,
    )
    feature = extrudes.add(extrude_input)
    feature.name = f"Estrusione_{body_name}"
    if operation == adsk.fusion.FeatureOperations.NewBodyFeatureOperation:
        feature.bodies.item(0).name = body_name
    return feature.bodies.item(0)


def _offset_yz_plane(component, offset_expression):
    if offset_expression in ("0", "0 mm"):
        return component.yZConstructionPlane
    plane_input = component.constructionPlanes.createInput()
    plane_input.setByOffset(
        component.yZConstructionPlane,
        adsk.core.ValueInput.createByString(offset_expression),
    )
    return component.constructionPlanes.add(plane_input)


def _offset_xz_plane(component, offset_expression):
    if offset_expression in ("0", "0 mm"):
        return component.xZConstructionPlane
    plane_input = component.constructionPlanes.createInput()
    plane_input.setByOffset(
        component.xZConstructionPlane,
        adsk.core.ValueInput.createByString(offset_expression),
    )
    return component.constructionPlanes.add(plane_input)


def _numeric_mm_expression(expression):
    text = str(expression).strip()
    if not text.lower().endswith("mm"):
        raise RuntimeError(
            f"La quota del piano verticale deve essere numerica in mm: {expression}"
        )
    return float(text[:-2].strip())


def _vertical_rectangle_prism_x(
    component,
    body_name,
    plane_x_expression,
    length_y_mm,
    height_z_mm,
    center_y_mm,
    center_z_mm,
    thickness_expression,
    operation=adsk.fusion.FeatureOperations.NewBodyFeatureOperation,
):
    """Crea una piastra verticale sul piano YZ ed estrude lungo +X."""
    plane = _offset_yz_plane(component, plane_x_expression)
    sketch = component.sketches.add(plane)
    sketch.name = f"Schizzo_{body_name}"
    plane_x_mm = _numeric_mm_expression(plane_x_expression)
    first_model_point = adsk.core.Point3D.create(
        _mm_to_cm(plane_x_mm),
        _mm_to_cm(center_y_mm - length_y_mm / 2.0),
        _mm_to_cm(center_z_mm - height_z_mm / 2.0),
    )
    second_model_point = adsk.core.Point3D.create(
        _mm_to_cm(plane_x_mm),
        _mm_to_cm(center_y_mm + length_y_mm / 2.0),
        _mm_to_cm(center_z_mm + height_z_mm / 2.0),
    )
    sketch.sketchCurves.sketchLines.addTwoPointRectangle(
        sketch.modelToSketchSpace(first_model_point),
        sketch.modelToSketchSpace(second_model_point),
    )
    if sketch.profiles.count != 1:
        raise RuntimeError(f"Profilo verticale non valido per {body_name}")

    extrudes = component.features.extrudeFeatures
    extrude_input = extrudes.createInput(sketch.profiles.item(0), operation)
    extent = adsk.fusion.DistanceExtentDefinition.create(
        adsk.core.ValueInput.createByString(thickness_expression)
    )
    extrude_input.setOneSideExtent(
        extent,
        adsk.fusion.ExtentDirections.PositiveExtentDirection,
    )
    feature = extrudes.add(extrude_input)
    feature.name = f"Estrusione_{body_name}"
    if operation == adsk.fusion.FeatureOperations.NewBodyFeatureOperation:
        feature.bodies.item(0).name = body_name
    return feature.bodies.item(0), plane


def _vertical_rectangle_prism_y(
    component,
    body_name,
    plane_y_expression,
    width_x_mm,
    height_z_mm,
    center_x_mm,
    center_z_mm,
    thickness_expression,
    operation=adsk.fusion.FeatureOperations.NewBodyFeatureOperation,
):
    """Crea una piastra verticale sul piano XZ ed estrude lungo +Y."""
    plane = _offset_xz_plane(component, plane_y_expression)
    sketch = component.sketches.add(plane)
    sketch.name = f"Schizzo_{body_name}"
    plane_y_mm = _numeric_mm_expression(plane_y_expression)
    first_model_point = adsk.core.Point3D.create(
        _mm_to_cm(center_x_mm - width_x_mm / 2.0),
        _mm_to_cm(plane_y_mm),
        _mm_to_cm(center_z_mm - height_z_mm / 2.0),
    )
    second_model_point = adsk.core.Point3D.create(
        _mm_to_cm(center_x_mm + width_x_mm / 2.0),
        _mm_to_cm(plane_y_mm),
        _mm_to_cm(center_z_mm + height_z_mm / 2.0),
    )
    sketch.sketchCurves.sketchLines.addTwoPointRectangle(
        sketch.modelToSketchSpace(first_model_point),
        sketch.modelToSketchSpace(second_model_point),
    )
    if sketch.profiles.count != 1:
        raise RuntimeError(f"Profilo verticale non valido per {body_name}")

    extrudes = component.features.extrudeFeatures
    extrude_input = extrudes.createInput(sketch.profiles.item(0), operation)
    extent = adsk.fusion.DistanceExtentDefinition.create(
        adsk.core.ValueInput.createByString(thickness_expression)
    )
    extrude_input.setOneSideExtent(
        extent,
        adsk.fusion.ExtentDirections.PositiveExtentDirection,
    )
    feature = extrudes.add(extrude_input)
    feature.name = f"Estrusione_{body_name}"
    if operation == adsk.fusion.FeatureOperations.NewBodyFeatureOperation:
        feature.bodies.item(0).name = body_name
    return feature.bodies.item(0), plane


def _cut_round_hole_x(
    component,
    plane_x_expression,
    diameter_mm,
    center_y_mm,
    center_z_mm,
    cut_depth_expression,
    hole_name,
):
    """Taglia un foro con asse X in una piastra verticale."""
    plane = _offset_yz_plane(component, plane_x_expression)
    sketch = component.sketches.add(plane)
    sketch.name = f"Schizzo_{hole_name}"
    plane_x_mm = _numeric_mm_expression(plane_x_expression)
    center_model_point = adsk.core.Point3D.create(
        _mm_to_cm(plane_x_mm),
        _mm_to_cm(center_y_mm),
        _mm_to_cm(center_z_mm),
    )
    sketch.sketchCurves.sketchCircles.addByCenterRadius(
        sketch.modelToSketchSpace(center_model_point),
        _mm_to_cm(diameter_mm) / 2.0,
    )
    if sketch.profiles.count != 1:
        raise RuntimeError(f"Profilo circolare verticale non valido per {hole_name}")

    extrudes = component.features.extrudeFeatures
    cut_input = extrudes.createInput(
        sketch.profiles.item(0),
        adsk.fusion.FeatureOperations.CutFeatureOperation,
    )
    extent = adsk.fusion.DistanceExtentDefinition.create(
        adsk.core.ValueInput.createByString(cut_depth_expression)
    )
    cut_input.setOneSideExtent(
        extent,
        adsk.fusion.ExtentDirections.PositiveExtentDirection,
    )
    feature = extrudes.add(cut_input)
    feature.name = hole_name
    return feature


def _cut_vertical_rectangle_x(
    component,
    plane_x_expression,
    length_y_mm,
    height_z_mm,
    center_y_mm,
    center_z_mm,
    cut_depth_expression,
    cut_name,
):
    """Taglia una finestra rettangolare con normale lungo +X."""
    plane = _offset_yz_plane(component, plane_x_expression)
    sketch = component.sketches.add(plane)
    sketch.name = f"Schizzo_{cut_name}"
    plane_x_mm = _numeric_mm_expression(plane_x_expression)
    first_model_point = adsk.core.Point3D.create(
        _mm_to_cm(plane_x_mm),
        _mm_to_cm(center_y_mm - length_y_mm / 2.0),
        _mm_to_cm(center_z_mm - height_z_mm / 2.0),
    )
    second_model_point = adsk.core.Point3D.create(
        _mm_to_cm(plane_x_mm),
        _mm_to_cm(center_y_mm + length_y_mm / 2.0),
        _mm_to_cm(center_z_mm + height_z_mm / 2.0),
    )
    sketch.sketchCurves.sketchLines.addTwoPointRectangle(
        sketch.modelToSketchSpace(first_model_point),
        sketch.modelToSketchSpace(second_model_point),
    )
    if sketch.profiles.count != 1:
        raise RuntimeError(f"Profilo finestra verticale non valido per {cut_name}")

    extrudes = component.features.extrudeFeatures
    cut_input = extrudes.createInput(
        sketch.profiles.item(0),
        adsk.fusion.FeatureOperations.CutFeatureOperation,
    )
    extent = adsk.fusion.DistanceExtentDefinition.create(
        adsk.core.ValueInput.createByString(cut_depth_expression)
    )
    cut_input.setOneSideExtent(
        extent,
        adsk.fusion.ExtentDirections.PositiveExtentDirection,
    )
    feature = extrudes.add(cut_input)
    feature.name = cut_name
    return feature


def _cut_vertical_rectangle_y(
    component,
    plane_y_expression,
    width_x_mm,
    height_z_mm,
    center_x_mm,
    center_z_mm,
    cut_depth_expression,
    cut_name,
):
    """Taglia una finestra rettangolare con normale lungo +Y."""
    plane = _offset_xz_plane(component, plane_y_expression)
    sketch = component.sketches.add(plane)
    sketch.name = f"Schizzo_{cut_name}"
    plane_y_mm = _numeric_mm_expression(plane_y_expression)
    first_model_point = adsk.core.Point3D.create(
        _mm_to_cm(center_x_mm - width_x_mm / 2.0),
        _mm_to_cm(plane_y_mm),
        _mm_to_cm(center_z_mm - height_z_mm / 2.0),
    )
    second_model_point = adsk.core.Point3D.create(
        _mm_to_cm(center_x_mm + width_x_mm / 2.0),
        _mm_to_cm(plane_y_mm),
        _mm_to_cm(center_z_mm + height_z_mm / 2.0),
    )
    sketch.sketchCurves.sketchLines.addTwoPointRectangle(
        sketch.modelToSketchSpace(first_model_point),
        sketch.modelToSketchSpace(second_model_point),
    )
    if sketch.profiles.count != 1:
        raise RuntimeError(f"Profilo finestra asse Y non valido per {cut_name}")

    extrudes = component.features.extrudeFeatures
    cut_input = extrudes.createInput(
        sketch.profiles.item(0),
        adsk.fusion.FeatureOperations.CutFeatureOperation,
    )
    extent = adsk.fusion.DistanceExtentDefinition.create(
        adsk.core.ValueInput.createByString(cut_depth_expression)
    )
    cut_input.setOneSideExtent(
        extent,
        adsk.fusion.ExtentDirections.PositiveExtentDirection,
    )
    feature = extrudes.add(cut_input)
    feature.name = cut_name
    return feature


def _cylinder_prism_x(
    component,
    body_name,
    plane_x_expression,
    diameter_mm,
    center_y_mm,
    center_z_mm,
    length_expression,
    operation=adsk.fusion.FeatureOperations.NewBodyFeatureOperation,
):
    """Crea un cilindro con asse X, usato per i due perni servo coassiali."""
    plane = _offset_yz_plane(component, plane_x_expression)
    sketch = component.sketches.add(plane)
    sketch.name = f"Schizzo_{body_name}"
    plane_x_mm = _numeric_mm_expression(plane_x_expression)
    center_model_point = adsk.core.Point3D.create(
        _mm_to_cm(plane_x_mm),
        _mm_to_cm(center_y_mm),
        _mm_to_cm(center_z_mm),
    )
    sketch.sketchCurves.sketchCircles.addByCenterRadius(
        sketch.modelToSketchSpace(center_model_point),
        _mm_to_cm(diameter_mm) / 2.0,
    )
    if sketch.profiles.count != 1:
        raise RuntimeError(f"Profilo circolare verticale non valido per {body_name}")

    extrudes = component.features.extrudeFeatures
    extrude_input = extrudes.createInput(sketch.profiles.item(0), operation)
    extent = adsk.fusion.DistanceExtentDefinition.create(
        adsk.core.ValueInput.createByString(length_expression)
    )
    extrude_input.setOneSideExtent(
        extent,
        adsk.fusion.ExtentDirections.PositiveExtentDirection,
    )
    feature = extrudes.add(extrude_input)
    feature.name = f"Estrusione_{body_name}"
    if operation == adsk.fusion.FeatureOperations.NewBodyFeatureOperation:
        feature.bodies.item(0).name = body_name
    return feature


def _cylinder_prism_y(
    component,
    body_name,
    plane_y_expression,
    diameter_mm,
    center_x_mm,
    center_z_mm,
    length_expression,
    operation=adsk.fusion.FeatureOperations.NewBodyFeatureOperation,
):
    """Crea un cilindro con asse Y per solenoide e canna tubolare."""
    plane = _offset_xz_plane(component, plane_y_expression)
    sketch = component.sketches.add(plane)
    sketch.name = f"Schizzo_{body_name}"
    plane_y_mm = _numeric_mm_expression(plane_y_expression)
    center_model_point = adsk.core.Point3D.create(
        _mm_to_cm(center_x_mm),
        _mm_to_cm(plane_y_mm),
        _mm_to_cm(center_z_mm),
    )
    sketch.sketchCurves.sketchCircles.addByCenterRadius(
        sketch.modelToSketchSpace(center_model_point),
        _mm_to_cm(diameter_mm) / 2.0,
    )
    if sketch.profiles.count != 1:
        raise RuntimeError(f"Profilo circolare asse Y non valido per {body_name}")

    extrudes = component.features.extrudeFeatures
    extrude_input = extrudes.createInput(sketch.profiles.item(0), operation)
    extent = adsk.fusion.DistanceExtentDefinition.create(
        adsk.core.ValueInput.createByString(length_expression)
    )
    extrude_input.setOneSideExtent(
        extent,
        adsk.fusion.ExtentDirections.PositiveExtentDirection,
    )
    feature = extrudes.add(extrude_input)
    feature.name = f"Estrusione_{body_name}"
    if operation == adsk.fusion.FeatureOperations.NewBodyFeatureOperation:
        feature.bodies.item(0).name = body_name
    return feature


def _cut_round_hole_y(
    component,
    plane_y_expression,
    diameter_mm,
    center_x_mm,
    center_z_mm,
    cut_depth_expression,
    hole_name,
):
    """Taglia un foro con asse Y, usato per i passaggi interni cilindrici."""
    plane = _offset_xz_plane(component, plane_y_expression)
    sketch = component.sketches.add(plane)
    sketch.name = f"Schizzo_{hole_name}"
    plane_y_mm = _numeric_mm_expression(plane_y_expression)
    center_model_point = adsk.core.Point3D.create(
        _mm_to_cm(center_x_mm),
        _mm_to_cm(plane_y_mm),
        _mm_to_cm(center_z_mm),
    )
    sketch.sketchCurves.sketchCircles.addByCenterRadius(
        sketch.modelToSketchSpace(center_model_point),
        _mm_to_cm(diameter_mm) / 2.0,
    )
    if sketch.profiles.count != 1:
        raise RuntimeError(f"Profilo foro asse Y non valido per {hole_name}")

    extrudes = component.features.extrudeFeatures
    cut_input = extrudes.createInput(
        sketch.profiles.item(0),
        adsk.fusion.FeatureOperations.CutFeatureOperation,
    )
    extent = adsk.fusion.DistanceExtentDefinition.create(
        adsk.core.ValueInput.createByString(cut_depth_expression)
    )
    cut_input.setOneSideExtent(
        extent,
        adsk.fusion.ExtentDirections.PositiveExtentDirection,
    )
    feature = extrudes.add(cut_input)
    feature.name = hole_name
    return feature


def _polygon_prism_x(
    component,
    body_name,
    plane_x_expression,
    points_yz_mm,
    thickness_expression,
):
    """Estrude lungo X un profilo poligonale definito come coppie (Y, Z)."""
    plane = _offset_yz_plane(component, plane_x_expression)
    sketch = component.sketches.add(plane)
    sketch.name = f"Schizzo_{body_name}"
    plane_x_mm = _numeric_mm_expression(plane_x_expression)
    points = [
        sketch.modelToSketchSpace(
            adsk.core.Point3D.create(
                _mm_to_cm(plane_x_mm),
                _mm_to_cm(y),
                _mm_to_cm(z),
            )
        )
        for y, z in points_yz_mm
    ]
    lines = sketch.sketchCurves.sketchLines
    for index in range(len(points)):
        lines.addByTwoPoints(points[index], points[(index + 1) % len(points)])
    if sketch.profiles.count != 1:
        raise RuntimeError(f"Profilo poligonale non valido per {body_name}")

    extrudes = component.features.extrudeFeatures
    extrude_input = extrudes.createInput(
        sketch.profiles.item(0),
        adsk.fusion.FeatureOperations.NewBodyFeatureOperation,
    )
    extent = adsk.fusion.DistanceExtentDefinition.create(
        adsk.core.ValueInput.createByString(thickness_expression)
    )
    extrude_input.setOneSideExtent(
        extent,
        adsk.fusion.ExtentDirections.PositiveExtentDirection,
    )
    feature = extrudes.add(extrude_input)
    feature.name = f"Estrusione_{body_name}"
    feature.bodies.item(0).name = body_name
    return feature.bodies.item(0)


def _cut_hex_pocket(
    component,
    plane,
    across_flats_mm,
    center_x_mm,
    center_y_mm,
    cut_depth_expression,
    pocket_name,
):
    sketch = component.sketches.add(plane)
    sketch.name = f"Schizzo_{pocket_name}"
    radius_mm = across_flats_mm / math.sqrt(3.0)
    points = []
    for index in range(6):
        angle = math.radians(30.0 + index * 60.0)
        points.append(
            adsk.core.Point3D.create(
                _mm_to_cm(center_x_mm + radius_mm * math.cos(angle)),
                _mm_to_cm(center_y_mm + radius_mm * math.sin(angle)),
                0,
            )
        )
    lines = sketch.sketchCurves.sketchLines
    for index in range(6):
        lines.addByTwoPoints(points[index], points[(index + 1) % 6])
    if sketch.profiles.count != 1:
        raise RuntimeError(f"Profilo esagonale non valido per {pocket_name}")

    extrudes = component.features.extrudeFeatures
    cut_input = extrudes.createInput(
        sketch.profiles.item(0),
        adsk.fusion.FeatureOperations.CutFeatureOperation,
    )
    extent = adsk.fusion.DistanceExtentDefinition.create(
        adsk.core.ValueInput.createByString(cut_depth_expression)
    )
    cut_input.setOneSideExtent(
        extent,
        adsk.fusion.ExtentDirections.PositiveExtentDirection,
    )
    cut_feature = extrudes.add(cut_input)
    cut_feature.name = pocket_name
    return cut_feature


def _prepare_battery_holder(design, data, include_standalone_bottom_parameter=True):
    holder = data["electronics"]["battery_holder"]
    dims = holder["confirmed_dimensions"]
    cable_exit = holder["cable_exit"]

    inner_length = dims["inner_length"]
    inner_width = dims["inner_width"]
    outer_length = dims["outer_length"]
    outer_width = dims["outer_width"]
    bottom_thickness = (
        dims["bottom_thickness"] if include_standalone_bottom_parameter else None
    )
    wall_thickness = dims["side_wall_thickness"]
    wall_height = dims["wall_height"]
    end_wall_thickness = outer_length - inner_length

    tolerance = 0.01
    if abs((outer_width - inner_width) - 2.0 * wall_thickness) > tolerance:
        raise RuntimeError(
            "Quote supporto batteria incoerenti: larghezza esterna - larghezza "
            "interna deve essere uguale a due pareti laterali."
        )
    if end_wall_thickness <= 0:
        raise RuntimeError(
            "Quote supporto batteria incoerenti: la lunghezza esterna deve "
            "superare quella interna."
        )

    parameter_specs = [
        ("batt_vano_lunghezza", inner_length, "Vano batteria"),
        ("batt_vano_larghezza", inner_width, "Vano batteria"),
        ("batt_esterno_lunghezza", outer_length, "Supporto batteria"),
        ("batt_esterno_larghezza", outer_width, "Supporto batteria"),
        ("batt_parete_spessore", wall_thickness, "Pareti laterali"),
        ("batt_parete_altezza", wall_height, "Pareti laterali"),
        ("batt_apertura_cavi", cable_exit["opening_length"], "Passaggio cavi"),
    ]
    if include_standalone_bottom_parameter:
        parameter_specs.append(
            (
                "batt_fondo_spessore",
                bottom_thickness,
                "Fondo della sola variante autonoma",
            )
        )
    for name, value, comment in parameter_specs:
        _add_user_parameter(design, name, value, "mm", comment)

    return dims, cable_exit, end_wall_thickness


def _add_battery_holder_walls(
    component,
    wall_plane,
    dims,
    cable_exit,
    end_wall_thickness,
    center_x_mm=0.0,
    center_y_mm=0.0,
    long_wall_side_override=None,
):
    """Aggiunge le pareti della vaschetta a un fondo già esistente."""
    outer_length = dims["outer_length"]
    outer_width = dims["outer_width"]
    wall_thickness = dims["side_wall_thickness"]
    wall_height = dims["wall_height"]
    wall_center_offset_x = (outer_width - wall_thickness) / 2.0

    for side_name, center_offset_x in (
        ("Ovest", -wall_center_offset_x),
        ("Est", wall_center_offset_x),
    ):
        _rectangle_prism_at(
            component,
            wall_plane,
            f"Parete_lunga_{side_name}",
            wall_thickness,
            outer_length,
            center_x_mm + center_offset_x,
            center_y_mm,
            "batt_parete_altezza",
            adsk.fusion.FeatureOperations.JoinFeatureOperation,
        )

    closed_end_center_y = (
        center_y_mm - outer_length / 2.0 + end_wall_thickness / 2.0
    )
    _rectangle_prism_at(
        component,
        wall_plane,
        "Parete_corta_chiusa",
        outer_width,
        end_wall_thickness,
        center_x_mm,
        closed_end_center_y,
        "batt_parete_altezza",
        adsk.fusion.FeatureOperations.JoinFeatureOperation,
    )

    exit_kind = cable_exit["kind"]
    opening_length = cable_exit["opening_length"]
    if exit_kind == "short_wall_center_window":
        _cut_rectangle(
            component,
            wall_plane,
            opening_length,
            end_wall_thickness + 0.2,
            center_x_mm,
            closed_end_center_y,
            "batt_parete_altezza",
            "Apertura_cavi_parete_corta_centrale",
        )
    elif exit_kind in (
        "both_long_walls_interior_end_gap",
        "one_long_wall_interior_end_gap",
    ):
        opening_end = cable_exit.get("opening_end")
        if opening_end == "south":
            # La luce utile inizia dopo la parete corta Sud: in questo modo
            # tutti i 10 mm sono accessibili dal vano interno.
            gap_center_y = (
                center_y_mm
                - outer_length / 2.0
                + end_wall_thickness
                + opening_length / 2.0
            )
        elif opening_end == "north":
            gap_center_y = (
                center_y_mm + outer_length / 2.0 - opening_length / 2.0
            )
        else:
            raise RuntimeError(
                "Per l'apertura della parete lunga indicare opening_end "
                "come 'south' oppure 'north'."
            )
        sides = (
            ("Ovest", center_x_mm - wall_center_offset_x),
            ("Est", center_x_mm + wall_center_offset_x),
        )
        if exit_kind == "one_long_wall_interior_end_gap":
            requested_side = (
                long_wall_side_override or cable_exit.get("long_wall_side")
            )
            if requested_side not in ("west", "east"):
                raise RuntimeError(
                    "Per one_long_wall_interior_end_gap indicare "
                    "electronics.battery_holder.cable_exit.long_wall_side "
                    "come 'west' oppure 'east'."
                )
            sides = tuple(
                item
                for item in sides
                if item[0] == ("Ovest" if requested_side == "west" else "Est")
            )
        for side_name, center_x in sides:
            _cut_rectangle(
                component,
                wall_plane,
                wall_thickness + 0.2,
                opening_length,
                center_x,
                gap_center_y,
                "batt_parete_altezza",
                f"Apertura_cavi_parete_lunga_{side_name}",
            )
    else:
        raise RuntimeError(
            "Tipo apertura cavi supporto batteria non riconosciuto. Usare "
            "'short_wall_center_window', "
            "'both_long_walls_interior_end_gap' oppure "
            "'one_long_wall_interior_end_gap'."
        )


def _create_battery_holder(
    document,
    design,
    root,
    data,
    long_wall_side_override=None,
):
    """Crea la variante autonoma con fondo da 2 mm."""
    dims, cable_exit, end_wall_thickness = _prepare_battery_holder(design, data)

    component = _new_component(root, "01_Supporto_batteria_parametrico")
    _centered_rectangle_prism(
        component,
        "Fondo_supporto_batteria",
        dims["outer_width"],
        dims["outer_length"],
        "batt_fondo_spessore",
    )
    wall_plane = _offset_plane(component, "batt_fondo_spessore")
    _add_battery_holder_walls(
        component,
        wall_plane,
        dims,
        cable_exit,
        end_wall_thickness,
        long_wall_side_override=long_wall_side_override,
    )

    if component.bRepBodies.count != 1:
        raise RuntimeError(
            "Il supporto batteria autonomo deve formare un solo corpo stampabile."
        )
    component.bRepBodies.item(0).name = "Supporto_batteria_con_apertura_cavi"
    return document, design


def _integrate_battery_holder_into_lower_deck(design, lower_component, data):
    """Usa il piano inferiore come fondo della vaschetta batteria."""
    _validate_lower_deck_layout(data)
    layout = data["electronics"]["lower_deck_layout"]["battery_holder"]
    dims, cable_exit, end_wall_thickness = _prepare_battery_holder(
        design,
        data,
        include_standalone_bottom_parameter=False,
    )
    wall_plane = _offset_plane(lower_component, "piano_inf_spessore")
    _add_battery_holder_walls(
        lower_component,
        wall_plane,
        dims,
        cable_exit,
        end_wall_thickness,
        center_x_mm=layout["center_x"],
        center_y_mm=layout["center_y"],
    )
    if lower_component.bRepBodies.count != 1:
        raise RuntimeError(
            "Piano inferiore e supporto batteria integrato devono formare un solo corpo."
        )
    lower_component.name = (
        "01_Piano_inferiore_colonnine_M3_supporto_batteria_integrato"
    )
    lower_component.bRepBodies.item(0).name = (
        "Piano_inferiore_colonnine_M3_supporto_batteria_integrato"
    )


def _translation_matrix(x_mm=0, y_mm=0, z_mm=0):
    transform = adsk.core.Matrix3D.create()
    transform.translation = adsk.core.Vector3D.create(
        _mm_to_cm(x_mm),
        _mm_to_cm(y_mm),
        _mm_to_cm(z_mm),
    )
    return transform


def _new_component_occurrence(root_component, name, transform=None):
    if transform is None:
        transform = adsk.core.Matrix3D.create()
    occurrence = root_component.occurrences.addNewComponent(transform)
    occurrence.component.name = name
    return occurrence, occurrence.component


def _create_arduino_plan_reference(design, root, data, z_mm):
    """Crea il riferimento XY esatto senza inventare l'altezza dei supporti."""
    arduino = data["electronics"]["arduino"]
    layout = data["electronics"]["lower_deck_layout"]["arduino_and_shield"]
    rotation = layout["rotation_deg_counterclockwise"]
    if abs((rotation % 360) - 90.0) > 1e-6:
        raise RuntimeError("Il riferimento Arduino richiede una rotazione di 90 gradi.")

    _add_user_parameter(
        design,
        "arduino_r4_lunghezza",
        arduino["length"],
        "mm",
        "Profilo ufficiale Arduino UNO R4 WiFi",
    )
    _add_user_parameter(
        design,
        "arduino_r4_larghezza",
        arduino["width"],
        "mm",
        "Profilo ufficiale Arduino UNO R4 WiFi",
    )
    _add_user_parameter(
        design,
        "arduino_r4_spessore_pcb",
        arduino["board_thickness"],
        "mm",
        "Spessore PCB ufficiale; quota Z di montaggio non ancora definita",
    )
    _add_user_parameter(
        design,
        "arduino_r4_rotazione",
        rotation,
        "deg",
        "Jack DC orientato verso Sud",
    )
    _add_user_parameter(
        design,
        "arduino_r4_centro_x",
        layout["center_x"],
        "mm",
        "Posizione planimetrica Arduino",
    )
    _add_user_parameter(
        design,
        "arduino_r4_centro_y",
        layout["center_y"],
        "mm",
        "Posizione planimetrica Arduino",
    )

    transform = _translation_matrix(layout["center_x"], layout["center_y"], z_mm)
    _, component = _new_component_occurrence(
        root,
        "05_Arduino_UNO_R4_WiFi_RIFERIMENTO_XY_quota_Z_da_definire",
        transform,
    )
    sketch = component.sketches.add(component.xYConstructionPlane)
    sketch.name = "Riferimento_planimetrico_Arduino_R4_no_supporti"
    half_width = _mm_to_cm(arduino["width"]) / 2.0
    half_length = _mm_to_cm(arduino["length"]) / 2.0
    sketch.sketchCurves.sketchLines.addTwoPointRectangle(
        adsk.core.Point3D.create(-half_width, -half_length, 0),
        adsk.core.Point3D.create(half_width, half_length, 0),
    )

    holes = arduino["mounting_holes"]
    if len(holes) != 4:
        raise RuntimeError("Il riferimento Arduino deve contenere quattro fori.")
    radius = _mm_to_cm(arduino["mounting_hole_diameter"]) / 2.0
    for hole in holes:
        original_x = hole.get("x")
        original_y = hole.get("y")
        if not isinstance(original_x, (int, float)) or not isinstance(
            original_y, (int, float)
        ):
            raise RuntimeError("Le coordinate dei fori Arduino devono essere numeriche.")
        centered_x = original_x - arduino["length"] / 2.0
        centered_y = original_y - arduino["width"] / 2.0
        rotated_x = -centered_y
        rotated_y = centered_x
        sketch.sketchCurves.sketchCircles.addByCenterRadius(
            adsk.core.Point3D.create(
                _mm_to_cm(rotated_x),
                _mm_to_cm(rotated_y),
                0,
            ),
            radius,
        )
    return component


def _add_as_built_rigid_joint(root, first, second, name):
    joint_input = root.asBuiltJoints.createInput(first, second, None)
    if not joint_input.setAsRigidJointMotion():
        raise RuntimeError(f"Impossibile definire il giunto rigido {name}")
    joint = root.asBuiltJoints.add(joint_input)
    if not joint:
        raise RuntimeError(f"Impossibile creare il giunto rigido {name}")
    joint.name = name
    return joint


def _add_as_built_revolute_joint(
    root,
    first,
    second,
    name,
    direction,
    joint_geometry,
    custom_axis=None,
    minimum_deg=None,
    maximum_deg=None,
):
    joint_input = root.asBuiltJoints.createInput(first, second, joint_geometry)
    if custom_axis:
        success = joint_input.setAsRevoluteJointMotion(direction, custom_axis)
    else:
        success = joint_input.setAsRevoluteJointMotion(direction)
    if not success:
        raise RuntimeError(f"Impossibile definire il giunto rotoidale {name}")
    joint = root.asBuiltJoints.add(joint_input)
    if not joint:
        raise RuntimeError(f"Impossibile creare il giunto rotoidale {name}")
    joint.name = name
    if minimum_deg is not None or maximum_deg is not None:
        motion = adsk.fusion.RevoluteJointMotion.cast(joint.jointMotion)
        if not motion:
            raise RuntimeError(f"Impossibile impostare i limiti del giunto {name}")
        limits = motion.rotationLimits
        if minimum_deg is not None:
            limits.minimumValue = math.radians(minimum_deg)
            limits.isMinimumValueEnabled = True
        if maximum_deg is not None:
            limits.maximumValue = math.radians(maximum_deg)
            limits.isMaximumValueEnabled = True
    return joint


def _validate_sketch_line_world_axis(
    sketch_line, expected_axis, name, tolerance=1e-3
):
    """Verifica in coordinate globali la linea usata come asse personalizzato."""
    world_line = sketch_line.worldGeometry
    if not world_line:
        raise RuntimeError(f"Fusion non restituisce l'asse globale {name}")
    start = world_line.startPoint
    end = world_line.endPoint
    dx = end.x - start.x
    dy = end.y - start.y
    dz = end.z - start.z
    magnitude = math.sqrt(dx * dx + dy * dy + dz * dz)
    if magnitude <= 1e-9:
        raise RuntimeError(f"La linea asse {name} ha lunghezza nulla")
    axis = adsk.core.Vector3D.create(
        dx / magnitude,
        dy / magnitude,
        dz / magnitude,
    )
    components = (abs(axis.x), abs(axis.y), abs(axis.z))
    expected = tuple(abs(value) for value in expected_axis)
    if any(abs(actual - wanted) > tolerance for actual, wanted in zip(components, expected)):
        raise RuntimeError(
            f"Asse errato per {name}: "
            f"({axis.x:.6f}, {axis.y:.6f}, {axis.z:.6f}), "
            f"atteso {expected_axis}"
        )
    return axis


def _create_continuous_hull_shell(design, root, data):
    """Crea il guscio laterale unico removibile attorno ai due piani del carro."""
    shell = data["hull_shell"]
    upper = data["chassis"]["upper_deck"]
    mounting_tabs = shell["mounting_tabs"]
    ventilation = shell["ventilation_grilles"]
    parameter_specs = (
        ("guscio_carro_larghezza_interna", shell["inner_width"], "Vano interno guscio carro"),
        ("guscio_carro_lunghezza_interna", shell["inner_length"], "Vano interno guscio carro"),
        ("guscio_carro_larghezza_esterna", shell["outer_width"], "Ingombro esterno guscio carro"),
        ("guscio_carro_lunghezza_esterna", shell["outer_length"], "Ingombro esterno guscio carro"),
        ("guscio_carro_parete", shell["wall_thickness"], "Pareti guscio removibile"),
        ("guscio_carro_altezza_inferiore", shell["lower_skirt_height"], "Da piano inferiore a sommità piano superiore"),
        ("guscio_carro_gioco_lato", shell["clearance_per_side"], "Gioco per lato rispetto ai piani"),
        (
            "guscio_carro_altezza_laterale_continua",
            shell["continuous_side_wall_height"],
            "Parete unica senza giunzione intermedia",
        ),
        (
            "guscio_linguetta_M2_5_spessore",
            mounting_tabs["vertical_thickness"],
            "Fissaggio guscio sotto il piano superiore",
        ),
        (
            "guscio_linguetta_M2_5_span",
            mounting_tabs["span_parallel_to_wall"],
            "Fissaggio guscio sotto il piano superiore",
        ),
        (
            "guscio_linguetta_M2_5_profondita",
            mounting_tabs["depth_from_wall"],
            "Fissaggio guscio sotto il piano superiore",
        ),
        (
            "guscio_linguetta_M2_5_preforo",
            mounting_tabs["printed_pilot_hole_diameter"],
            "Preforo per M2.5x8",
        ),
        (
            "griglia_feritoie_per_parete",
            ventilation["slot_count_per_wall"],
            "Numero ridotto di feritoie fronte e retro",
        ),
        (
            "griglia_feritoia_larghezza",
            ventilation["slot_width"],
            "Ventilazione vano inferiore",
        ),
        (
            "griglia_feritoia_altezza",
            ventilation["slot_height"],
            "Ventilazione vano inferiore",
        ),
        (
            "griglia_feritoia_passo_verticale",
            ventilation["vertical_pitch"],
            "Ventilazione vano inferiore",
        ),
    )
    for name, value, comment in parameter_specs:
        _add_user_parameter(design, name, value, "mm", comment)

    occurrence, component = _new_component_occurrence(
        root,
        "03_Guscio_laterale_continuo_carro",
    )
    zero_plane = _offset_plane(component, "0 mm")
    long_wall_center_x = (
        shell["outer_width"] - shell["wall_thickness"]
    ) / 2.0
    short_wall_center_y = (
        shell["outer_length"] - shell["wall_thickness"]
    ) / 2.0

    _rectangle_prism_at(
        component,
        zero_plane,
        "Parete_guscio_Ovest",
        shell["wall_thickness"],
        shell["outer_length"],
        -long_wall_center_x,
        0,
        "guscio_carro_altezza_laterale_continua",
    )
    _rectangle_prism_at(
        component,
        zero_plane,
        "Parete_guscio_Sud",
        shell["outer_width"],
        shell["wall_thickness"],
        0,
        -short_wall_center_y,
        "guscio_carro_altezza_laterale_continua",
        adsk.fusion.FeatureOperations.JoinFeatureOperation,
    )
    _rectangle_prism_at(
        component,
        zero_plane,
        "Parete_guscio_Est",
        shell["wall_thickness"],
        shell["outer_length"],
        long_wall_center_x,
        0,
        "guscio_carro_altezza_laterale_continua",
        adsk.fusion.FeatureOperations.JoinFeatureOperation,
    )
    _rectangle_prism_at(
        component,
        zero_plane,
        "Parete_guscio_Nord",
        shell["outer_width"],
        shell["wall_thickness"],
        0,
        short_wall_center_y,
        "guscio_carro_altezza_laterale_continua",
        adsk.fusion.FeatureOperations.JoinFeatureOperation,
    )

    # Tre feritoie larghe sul fronte Nord e tre sul retro Sud. Sono nel vano
    # inferiore, lontane dai piani e dalle linguette, e mantengono legamenti da
    # 4 mm adatti a una normale stampa FDM.
    grille_count = ventilation["slot_count_per_wall"]
    grille_first_z = (
        ventilation["center_z"]
        - (grille_count - 1) * ventilation["vertical_pitch"] / 2.0
    )
    grille_planes = (
        ("Posteriore_Sud", -shell["outer_length"] / 2.0),
        ("Anteriore_Nord", shell["inner_length"] / 2.0),
    )
    for wall_name, plane_y in grille_planes:
        for slot_index in range(grille_count):
            slot_center_z = grille_first_z + slot_index * ventilation["vertical_pitch"]
            _cut_vertical_rectangle_y(
                component,
                f"{plane_y} mm",
                ventilation["slot_width"],
                ventilation["slot_height"],
                ventilation["center_x"],
                slot_center_z,
                f"{shell['wall_thickness'] + 0.2} mm",
                f"Griglia_{wall_name}_{slot_index + 1:02d}",
            )

    tab_bottom_z = (
        shell["split_z"]
        - upper["thickness"]
        - mounting_tabs["vertical_thickness"]
    )
    tab_plane = _offset_plane(component, f"{tab_bottom_z} mm")
    for index, tab in enumerate(mounting_tabs["positions"], start=1):
        if tab["wall"] in ("south", "north"):
            tab_width = mounting_tabs["span_parallel_to_wall"]
            tab_length = mounting_tabs["depth_from_wall"]
        else:
            tab_width = mounting_tabs["depth_from_wall"]
            tab_length = mounting_tabs["span_parallel_to_wall"]
        label = f"{index:02d}_{tab['name']}"
        _rectangle_prism_at(
            component,
            tab_plane,
            f"Linguetta_M2_5_{label}",
            tab_width,
            tab_length,
            tab["x"],
            tab["y"],
            f"{mounting_tabs['vertical_thickness']} mm",
            adsk.fusion.FeatureOperations.JoinFeatureOperation,
        )
        _cut_round_hole(
            component,
            tab_plane,
            mounting_tabs["printed_pilot_hole_diameter"],
            tab["x"],
            tab["y"],
            f"{mounting_tabs['vertical_thickness']} mm",
            f"Preforo_M2_5_guscio_{label}",
        )
    component.bRepBodies.item(0).name = (
        "Guscio_laterale_continuo_166x176_Z0_Z76_griglie_fronte_retro"
    )
    return occurrence


def _create_cover_and_modular_turret(document, design, root, data):
    cover = data["electronics_cover"]
    turret = data["turret"]
    stepper = turret["stepper"]
    rotating = turret["rotating_base"]
    azimuth_support = turret["azimuth_support"]
    frame = turret["elevation_frame"]
    servo = turret["servo"]
    cannon = turret["cannon"]
    firing = turret["firing_module"]
    loader = turret["manual_loader"]
    cable = turret["cable_routing"]
    roof_support = cover["central_roof_support"]
    adapter_mount_centers = (
        (-rotating["mounting_radius"], 0.0),
        (rotating["mounting_radius"], 0.0),
        (0.0, -rotating["mounting_radius"]),
        (0.0, rotating["mounting_radius"]),
    )
    fixed_anchor_specs = (
        ("Servo_sinistro", -28.0, -15.0),
        # Spostato a Nord rispetto al distanziale M3 Sud in (0,-19): nella
        # posizione precedente la prima asola intersecava il suo Ø10.
        ("Cannone", 0.0, -7.0),
        ("Servo_destro", 28.0, -15.0),
    )

    clearance = cable["routing_clearance_per_side"]
    required_common_width = max(
        cable["servo_connector_width"],
        cable["cannon_connector_width"],
    ) + 2.0 * clearance
    required_common_length = max(
        cable["servo_connector_thickness"]
        + (cable["servo_cable_count"] - 1)
        * cable["servo_cable_profile_thickness"],
        cable["cannon_connector_thickness"]
        + cable["servo_cable_count"]
        * cable["servo_cable_profile_thickness"],
    ) + 2.0 * clearance
    if cable["common_connector_passage_width"] < required_common_width or cable[
        "common_connector_passage_length"
    ] < required_common_length:
        raise RuntimeError(
            "Passaggio comune insufficiente per infilare in sequenza due connettori "
            "SG90 e il connettore cannone con i cavi gia presenti"
        )
    if cable["cannon_mobile_passage_width"] < (
        cable["cannon_connector_width"] + 2.0 * clearance
    ) or cable["cannon_mobile_passage_length"] < (
        cable["cannon_connector_thickness"] + 2.0 * clearance
    ):
        raise RuntimeError(
            "Passaggio mobile insufficiente per il connettore del cannone"
        )
    arc_inner_radius = (
        cable["azimuth_arc_mean_radius"]
        - cable["azimuth_arc_radial_width"] / 2.0
    )
    arc_outer_radius = (
        cable["azimuth_arc_mean_radius"]
        + cable["azimuth_arc_radial_width"] / 2.0
    )
    if arc_inner_radius <= stepper["overall_tab_width"] / 2.0:
        raise RuntimeError(
            "La guida arcuata dei cavi interferisce con le alette dello stepper"
        )
    if arc_outer_radius >= rotating["diameter"] / 2.0:
        raise RuntimeError(
            "La guida arcuata dei cavi supera il bordo dell'adattatore rotante"
        )
    channel_floor_top = (
        roof_support["channel_floor_bottom_z"]
        + roof_support["channel_floor_thickness"]
    )
    actual_channel_clearance = cover["wall_height"] - channel_floor_top
    if abs(
        actual_channel_clearance - roof_support["channel_clearance_height"]
    ) > 1e-6 or actual_channel_clearance < cable[
        "common_connector_passage_length"
    ]:
        raise RuntimeError(
            "Il canale anulare non lascia altezza sufficiente ai connettori."
        )
    if (
        roof_support["channel_floor_inner_radius"]
        <= stepper["body_diameter"] / 2.0
        or roof_support["channel_floor_inner_radius"] >= arc_inner_radius
    ):
        raise RuntimeError(
            "Il foro interno del fondo anulare deve liberare lo stepper e iniziare "
            "prima della pista cavi."
        )
    channel_inner_wall_face = (
        arc_inner_radius - roof_support["channel_wall_thickness"]
    )
    if channel_inner_wall_face <= (
        stepper["overall_tab_width"] / 2.0 + clearance
    ):
        raise RuntimeError(
            "La parete interna liscia del canale interferisce con le alette stepper."
        )
    if roof_support["channel_floor_outer_radius"] < (
        arc_outer_radius + roof_support["channel_wall_thickness"]
    ):
        raise RuntimeError(
            "Il fondo anulare non raggiunge la parete esterna della pista cavi."
        )
    if cable["azimuth_arc_radial_width"] < cable["common_connector_passage_width"]:
        raise RuntimeError(
            "La guida arcuata deve essere larga almeno quanto il passaggio connettori"
        )
    adapter_fastener_outer_radius = max(
        rotating["mounting_hole_diameter"] / 2.0,
        rotating["nut_across_flats"] / math.sqrt(3.0),
    )
    if rotating["mounting_radius"] + adapter_fastener_outer_radius >= (
        arc_inner_radius - 0.1
    ):
        raise RuntimeError(
            "Viti e dadi della base rotante devono restare interamente dentro la pista cavi."
        )
    expected_bore_diameter = (
        stepper["shaft_diameter"]
        + 2.0 * rotating["shaft_fit_clearance_per_side"]
    )
    expected_bore_flat = (
        stepper["shaft_flat_to_flat"]
        + 2.0 * rotating["shaft_fit_clearance_per_side"]
    )
    if abs(rotating["shaft_bore_diameter"] - expected_bore_diameter) > 1e-6:
        raise RuntimeError("Il diametro della sede D non rispetta il gioco parametrico.")
    if abs(rotating["shaft_bore_flat_to_flat"] - expected_bore_flat) > 1e-6:
        raise RuntimeError("La quota tra i piatti della sede doppia-D non rispetta il gioco.")
    if rotating["shaft_bore_flat_to_flat"] >= rotating["shaft_bore_diameter"]:
        raise RuntimeError("La sede doppia-D deve conservare due veri lati piatti.")
    if not (
        stepper["mounting_hole_diameter"]
        < stepper["mounting_countersink_diameter"]
    ):
        raise RuntimeError("La svasatura M4 deve essere più larga del foro passante.")
    if not (
        0.0
        < stepper["mounting_countersink_depth"]
        <= cover["roof_thickness"] - 0.6
    ):
        raise RuntimeError(
            "La svasatura M4 deve restare nel tetto lasciando almeno 0.6 mm."
        )

    washer_inner_radius = azimuth_support["thrust_washer_inner_diameter"] / 2.0
    washer_outer_radius = azimuth_support["thrust_washer_outer_diameter"] / 2.0
    washer_seat_depth = azimuth_support["thrust_washer_seat_depth"]
    washer_seat_clearance = azimuth_support[
        "thrust_washer_seat_radial_clearance_per_side"
    ]
    if not (0.0 < washer_seat_depth < cover["roof_thickness"] / 2.0):
        raise RuntimeError("La sede della rondella deve essere un ribasso superficiale.")
    if not (0.0 < washer_seat_clearance <= 0.5):
        raise RuntimeError("Il gioco radiale della sede rondella non è stampabile.")
    if washer_inner_radius <= (
        arc_outer_radius + roof_support["channel_wall_thickness"] + 1.0
    ):
        raise RuntimeError("L'appoggio assiale deve restare fuori dalla pista cavi.")
    if washer_outer_radius >= rotating["diameter"] / 2.0 - 1.0:
        raise RuntimeError("La rondella assiale deve restare sotto la base rotante.")
    if not (
        arc_outer_radius + 1.0
        < azimuth_support["fixed_guide_inner_radius"]
        < azimuth_support["fixed_guide_outer_radius"]
        < washer_inner_radius
    ):
        raise RuntimeError("Guida radiale, pista cavi e rondella assiale interferiscono.")
    guide_groove_inner = (
        azimuth_support["fixed_guide_inner_radius"]
        - azimuth_support["rotating_groove_radial_clearance_per_side"]
    )
    guide_groove_outer = (
        azimuth_support["fixed_guide_outer_radius"]
        + azimuth_support["rotating_groove_radial_clearance_per_side"]
    )
    if guide_groove_outer >= washer_inner_radius:
        raise RuntimeError("La gola di centraggio invade la rondella assiale.")
    adapter_gap_above_roof = (
        azimuth_support["thrust_washer_thickness"] - washer_seat_depth
    )
    hub_wall = (
        rotating["coupling_hub_outer_diameter"]
        - rotating["shaft_bore_diameter"]
    ) / 2.0
    if hub_wall < 2.0:
        raise RuntimeError("Il mozzo doppia-D deve avere almeno 2 mm di parete radiale.")
    hub_bottom_clearance_above_stepper = (
        cover["roof_thickness"]
        + adapter_gap_above_roof
        - rotating["coupling_hub_height_below_base"]
    )
    if hub_bottom_clearance_above_stepper < 0.8:
        raise RuntimeError(
            "Il mozzo rotante deve lasciare almeno 0.8 mm sopra la faccia dello stepper."
        )
    guide_nominal_engagement = (
        azimuth_support["fixed_guide_height"] - adapter_gap_above_roof
    )
    guide_engagement_at_full_lift = (
        guide_nominal_engagement
        - azimuth_support["anti_lift_vertical_clearance"]
    )
    if guide_engagement_at_full_lift < azimuth_support[
        "minimum_guide_engagement_at_full_lift"
    ]:
        raise RuntimeError(
            "La guida radiale può uscire dalla gola al massimo sollevamento."
        )
    if (
        azimuth_support["rotating_groove_depth"] - guide_nominal_engagement
        < 0.3
    ):
        raise RuntimeError(
            "La gola deve lasciare almeno 0.3 mm sopra il labbro di guida."
        )
    shaft_engagement = (
        stepper["shaft_length"]
        - hub_bottom_clearance_above_stepper
    )
    if shaft_engagement < rotating["minimum_shaft_engagement"]:
        raise RuntimeError(
            "La sede doppia-D deve impegnare almeno "
            f"{rotating['minimum_shaft_engagement']:.1f} mm dell'albero stepper."
        )
    anchor_half_x = cable["cable_tie_slot_length"] / 2.0
    anchor_half_y = cable["cable_tie_slot_width"] / 2.0
    frame_standoff_radius = azimuth_support["upper_frame_standoff_diameter"] / 2.0
    for anchor_name, anchor_x, anchor_y in fixed_anchor_specs:
        for y_sign in (-1.0, 1.0):
            slot_y = anchor_y + y_sign * cable["cable_tie_pair_spacing"] / 2.0
            for mount_x, mount_y in adapter_mount_centers:
                delta_x = max(abs(mount_x - anchor_x) - anchor_half_x, 0.0)
                delta_y = max(abs(mount_y - slot_y) - anchor_half_y, 0.0)
                if math.hypot(delta_x, delta_y) <= frame_standoff_radius + 0.2:
                    raise RuntimeError(
                        f"Asola fermacavo {anchor_name} interferisce con un "
                        "distanziale M3 della base rotante."
                    )
    if azimuth_support["anti_lift_clip_count"] != 4:
        raise RuntimeError("La revisione assemblabile usa quattro fermagli anti-sollevamento.")
    if azimuth_support["anti_lift_foot_inner_radius"] <= rotating["diameter"] / 2.0:
        raise RuntimeError("I piedi dei fermagli devono restare fuori dal disco rotante.")
    if azimuth_support["upper_frame_standoff_height"] <= (
        azimuth_support["anti_lift_vertical_clearance"]
        + azimuth_support["anti_lift_cap_thickness"]
    ):
        raise RuntimeError(
            "I distanziali del telaio devono sollevarlo sopra i fermagli fissi."
        )
    frame_to_clip_clearance = (
        azimuth_support["upper_frame_standoff_height"]
        - azimuth_support["anti_lift_vertical_clearance"]
        - azimuth_support["anti_lift_cap_thickness"]
    )
    if frame_to_clip_clearance < azimuth_support[
        "minimum_frame_to_clip_dynamic_clearance"
    ]:
        raise RuntimeError(
            "Il telaio rotante non ha margine FDM sufficiente sopra i fermagli."
        )
    if (
        azimuth_support["anti_lift_key_height"] <= 0
        or azimuth_support["anti_lift_key_width"] < 1.2
        or azimuth_support["anti_lift_key_side_clearance"] < 0.2
    ):
        raise RuntimeError("Gli spallamenti antirotazione dei fermagli non sono robusti.")
    if azimuth_support["anti_lift_screw_radius"] >= min(
        cover["outer_width"], cover["outer_length"]
    ) / 2.0 - 8.0:
        raise RuntimeError("Le viti dei fermagli sono troppo vicine al bordo del tetto.")
    full_annular_path = cable["azimuth_arc_sweep_deg"] >= 360.0 - 1e-6
    if cable["azimuth_rotation_range_deg"] >= 360.0 - 1e-6:
        if not full_annular_path:
            raise RuntimeError(
                "La corsa da -180 a +180 gradi richiede una guida anulare completa."
            )
    else:
        if abs(
            cable["rotating_passage_center_angle_deg"]
            - (
                cable["azimuth_arc_start_deg"]
                + cable["azimuth_arc_sweep_deg"] / 2.0
            )
        ) > 1e-6:
            raise RuntimeError(
                "Il passaggio rotante deve essere centrato nella corsa della guida arcuata"
            )
        required_arc_margin_deg = math.degrees(
            math.atan2(
                cable["common_connector_passage_length"] / 2.0,
                arc_inner_radius,
            )
        )
        required_arc_sweep_deg = (
            cable["azimuth_rotation_range_deg"] + 2.0 * required_arc_margin_deg
        )
        if cable["azimuth_arc_sweep_deg"] + 1e-3 < required_arc_sweep_deg:
            raise RuntimeError(
                "La guida cavi non copre il rettangolo di passaggio ai due estremi "
                "della corsa di azimut"
            )

    lower_anchor_half_x = cable["fixed_lower_anchor_pad_width"] / 2.0
    lower_anchor_half_y = cable["fixed_lower_anchor_pad_length"] / 2.0
    lower_anchor_near_radius = math.hypot(
        max(abs(cable["fixed_lower_anchor_pad_center_x"]) - lower_anchor_half_x, 0.0),
        max(abs(cable["fixed_lower_anchor_pad_center_y"]) - lower_anchor_half_y, 0.0),
    )
    if lower_anchor_near_radius >= roof_support["channel_floor_outer_radius"]:
        raise RuntimeError(
            "La piastrina fermacavo fissa inferiore non si unisce al fondo anulare."
        )
    if cable["fixed_lower_anchor_pad_thickness"] > roof_support[
        "channel_floor_bottom_z"
    ]:
        raise RuntimeError("La piastrina fermacavo fissa invade il volume inferiore.")
    if cable["cable_tie_slot_length"] > cable["fixed_lower_anchor_pad_width"] - 2.0:
        raise RuntimeError("Le asole non entrano nella piastrina fermacavo fissa.")
    lower_anchor_slot_x = (
        cable["fixed_lower_anchor_pad_center_x"]
        + cable["fixed_lower_anchor_slot_offset_x"]
    )
    for y_sign in (-1.0, 1.0):
        lower_anchor_slot_y = (
            cable["fixed_lower_anchor_pad_center_y"]
            + y_sign * cable["cable_tie_pair_spacing"] / 2.0
        )
        slot_near_radius = math.hypot(
            max(abs(lower_anchor_slot_x) - cable["cable_tie_slot_length"] / 2.0, 0.0),
            max(abs(lower_anchor_slot_y) - cable["cable_tie_slot_width"] / 2.0, 0.0),
        )
        if slot_near_radius < (
            roof_support["channel_floor_outer_radius"]
            + cable["fixed_lower_anchor_min_ligament"]
        ):
            raise RuntimeError(
                "Le asole del fermacavo fisso lasciano troppo poco materiale "
                "fuori dal fondo anulare."
            )
    pad_min_x = cable["fixed_lower_anchor_pad_center_x"] - lower_anchor_half_x
    pad_max_x = cable["fixed_lower_anchor_pad_center_x"] + lower_anchor_half_x
    pad_min_y = cable["fixed_lower_anchor_pad_center_y"] - lower_anchor_half_y
    pad_max_y = cable["fixed_lower_anchor_pad_center_y"] + lower_anchor_half_y
    bridge_half_x = cable["fixed_lower_anchor_bridge_width"] / 2.0
    bridge_half_y = cable["fixed_lower_anchor_bridge_length"] / 2.0
    bridge_min_x = cable["fixed_lower_anchor_bridge_center_x"] - bridge_half_x
    bridge_max_x = cable["fixed_lower_anchor_bridge_center_x"] + bridge_half_x
    bridge_min_y = cable["fixed_lower_anchor_bridge_center_y"] - bridge_half_y
    bridge_max_y = cable["fixed_lower_anchor_bridge_center_y"] + bridge_half_y
    overlap_x = min(pad_max_x, bridge_max_x) - max(pad_min_x, bridge_min_x)
    overlap_y = min(pad_max_y, bridge_max_y) - max(pad_min_y, bridge_min_y)
    if overlap_x < 3.0 or overlap_y < 3.0:
        raise RuntimeError("Il ponte del fermacavo non si unisce robustamente alla piastrina.")
    bridge_near_radius = math.hypot(
        max(abs(cable["fixed_lower_anchor_bridge_center_x"]) - bridge_half_x, 0.0),
        max(abs(cable["fixed_lower_anchor_bridge_center_y"]) - bridge_half_y, 0.0),
    )
    if bridge_near_radius > roof_support["channel_floor_outer_radius"] - 5.0:
        raise RuntimeError("Il ponte del fermacavo non entra abbastanza nel fondo anulare.")
    exit_angle = math.radians(cable["rotating_passage_center_angle_deg"])
    exit_center_y = cable["azimuth_arc_mean_radius"] * math.sin(exit_angle)
    exit_y_extent = (
        abs(math.sin(exit_angle)) * cable["common_connector_passage_width"] / 2.0
        + abs(math.cos(exit_angle)) * cable["common_connector_passage_length"] / 2.0
    )
    if bridge_min_y < exit_center_y + exit_y_extent + 2.0:
        raise RuntimeError("Il ponte del fermacavo ostruisce l'uscita fissa 9x7.")

    nominal_ear_projection = (
        servo["mounting_flange_overall_length"] - servo["body_length"]
    ) / 2.0
    if abs(nominal_ear_projection - servo["mounting_ear_projection_nominal"]) > 0.3:
        raise RuntimeError("La sporgenza delle alette SG90 non coincide con l'ingombro totale.")
    servo_ear_hole_offset_y = (
        servo["mounting_flange_overall_length"] / 2.0
        - servo["mounting_ear_hole_diameter"] / 2.0
        - servo["mounting_ear_free_edge_ligament"]
    )
    ear_inner_ligament = (
        servo_ear_hole_offset_y
        - servo["body_length"] / 2.0
        - servo["mounting_ear_hole_diameter"] / 2.0
    )
    if ear_inner_ligament < 1.2:
        raise RuntimeError("Il foro M2.5 lascia troppo poco materiale verso il corpo SG90.")
    if (
        servo["mounting_wall_slot_width"]
        < servo["mounting_ear_hole_diameter"] + 0.3
        or servo["mounting_wall_slot_length"]
        < servo["mounting_wall_slot_width"] + 1.0
    ):
        raise RuntimeError("Le asole regolabili M2.5 delle alette SG90 sono insufficienti.")
    servo_center_y = (
        servo["body_length"] / 2.0
        - servo["shaft_center_from_rear_body_end"]
    )
    servo_window_length = (
        servo["body_length"] + 2.0 * servo["fit_clearance_per_side"]
    )
    servo_window_min_y = servo_center_y - servo_window_length / 2.0
    south_ear_hole_y = servo_center_y - servo_ear_hole_offset_y
    servo_slot_outward_shift = (
        south_ear_hole_y
        + servo["mounting_wall_slot_length"] / 2.0
        - servo_window_min_y
        + servo["mounting_wall_min_web"]
    )
    slot_inboard_reach = (
        servo["mounting_wall_slot_length"] / 2.0
        - servo_slot_outward_shift
    )
    if slot_inboard_reach < servo["mounting_ear_hole_diameter"] / 2.0 + 0.05:
        raise RuntimeError(
            "L'asola aletta SG90 non contiene il foro M2.5 conservando la parete minima."
        )
    mobile_width = (
        frame["width"]
        - 2.0 * frame["wall_thickness"]
        - 2.0 * frame["mobile_side_clearance"]
    )
    if mobile_width < firing["pcb_width"] + 4.0:
        raise RuntimeError("La culla regolabile deve lasciare almeno 2 mm per lato alla PCB.")
    horn_adapter_radius = servo["horn_adapter_disc_diameter"] / 2.0
    if servo["horn_reference_span"] > servo["horn_adapter_disc_diameter"]:
        raise RuntimeError("Il disco adattatore non contiene l'inviluppo del cornetto a croce.")
    if not (
        frame["pivot_above_base_top"] - horn_adapter_radius >= 3.0
        and frame["pivot_above_base_top"] + horn_adapter_radius
        <= frame["height"] - 1.0
    ):
        raise RuntimeError("Il disco del cornetto non entra nel telaio di elevazione.")
    frame_inner_half_width = frame["width"] / 2.0 - frame["wall_thickness"]
    horn_axial_gap = frame_inner_half_width - servo["horn_adapter_outer_face_abs_x"]
    if horn_axial_gap < (
        servo["shaft_protrusion"] + servo["horn_reference_thickness"] + 0.2
    ):
        raise RuntimeError("Manca spazio assiale fra SG90, cornetto e adattatore mobile.")
    mobile_half_width = mobile_width / 2.0
    horn_disc_inner_face_abs_x = (
        servo["horn_adapter_outer_face_abs_x"]
        - servo["horn_adapter_disc_thickness"]
    )
    if abs(horn_disc_inner_face_abs_x - mobile_half_width) > 0.1:
        raise RuntimeError("Disco cornetto e bordo culla devono incontrarsi senza sovrapporsi.")
    if not (
        servo["horn_adapter_shelf_inner_x_abs"] < mobile_half_width
        and servo["horn_adapter_tray_pilot_depth"]
        <= frame["mobile_plate_thickness"] - 1.0
    ):
        raise RuntimeError("Mensola regolabile o preforo della culla non sono assemblabili.")
    if (
        servo["horn_adapter_adjustment_slot_width"] < 2.9
        or servo["horn_adapter_adjustment_slot_length"]
        < servo["horn_adapter_adjustment_slot_width"] + 1.0
    ):
        raise RuntimeError("Le asole degli adattatori cornetto non lasciano registrazione utile.")

    required_loader_bore = (
        loader["provisional_max_projectile_diameter"]
        + 2.0 * loader["projectile_radial_clearance"]
    )
    if loader["guide_inner_diameter"] + 1e-6 < required_loader_bore:
        raise RuntimeError("La guida di ricarica non lascia il gioco radiale previsto.")
    if loader["guide_inner_diameter"] > firing["barrel_inner_diameter"] + 1e-6:
        raise RuntimeError("La guida di ricarica non deve superare il foro interno della canna.")
    guide_wall = (
        loader["guide_outer_diameter"] - loader["guide_inner_diameter"]
    ) / 2.0
    if guide_wall < loader["minimum_printed_wall"]:
        raise RuntimeError("La parete della guida di ricarica è troppo sottile per FDM.")
    if loader["guide_length"] > 12.0:
        raise RuntimeError("La guida di ricarica supera lo spazio libero dietro al solenoide.")
    if loader["rear_window_width"] > 14.0:
        raise RuntimeError("La finestra di culatta indebolisce troppo la parete posteriore.")
    if loader["rear_window_width"] < loader["guide_outer_diameter"] + 0.8:
        raise RuntimeError("La finestra di culatta non libera la guida con margine FDM.")
    if loader["hatch_top_pocket_width"] < (
        loader["rear_window_width"] + 2.0 * loader["minimum_printed_wall"]
    ):
        raise RuntimeError("Il coperchio culatta non sovrappone abbastanza la finestra.")
    if loader["hatch_top_pocket_length"] < (
        loader["roof_slot_length"] + 2.0 * loader["minimum_printed_wall"]
    ):
        raise RuntimeError("Il coperchio culatta non sovrappone abbastanza l'asola tetto.")
    if not (
        0.0 < loader["countersink_depth"]
        <= loader["hatch_top_plate_thickness"] - 0.4
    ):
        raise RuntimeError("La svasatura M2.5 del coperchio deve lasciare almeno 0.4 mm.")
    if not (
        loader["hatch_top_plate_thickness"]
        + loader["hatch_vertical_clearance"]
        <= loader["hatch_top_pocket_depth"]
        < servo["holder_wall_thickness"]
    ):
        raise RuntimeError("La tasca culatta non lascia il gioco verticale previsto.")
    effective_roof_skin = (
        servo["holder_wall_thickness"]
        - loader["hatch_top_pocket_depth"]
        + loader["hatch_local_reinforcement_thickness"]
    )
    if effective_roof_skin < loader["minimum_printed_wall"]:
        raise RuntimeError("La tasca culatta lascia una soletta inferiore troppo sottile.")
    expected_vertical_plate = (
        servo["holder_wall_thickness"]
        - 2.0 * loader["hatch_clearance_per_side"]
    )
    if abs(loader["hatch_vertical_plate_thickness"] - expected_vertical_plate) > 1e-6:
        raise RuntimeError("Il coperchio posteriore non rispetta il gioco FDM sui due lati.")
    if loader["hatch_local_reinforcement_length"] + 1e-6 < loader[
        "hatch_top_pocket_length"
    ]:
        raise RuntimeError("Il rinforzo locale non copre tutta la tasca culatta.")
    if loader["guide_roof_rib_overlap"] < loader["minimum_printed_wall"]:
        raise RuntimeError("La nervatura della guida culatta ha troppo poco impegno.")
    if (
        loader["guide_outer_diameter"] / 2.0
        - loader["guide_roof_rib_overlap"]
        <= loader["guide_inner_diameter"] / 2.0 + 0.2
    ):
        raise RuntimeError("La nervatura della culatta invade il foro guida.")
    loader_screw_x = loader["mounting_hole_spacing"] / 2.0
    loader_boss_radius = loader["screw_boss_diameter"] / 2.0
    loader_head_radius = loader["countersink_diameter"] / 2.0
    if loader_screw_x - loader_head_radius < (
        loader["rear_window_width"] / 2.0 + loader["minimum_printed_wall"]
    ):
        raise RuntimeError("Le viti del coperchio culatta sono troppo vicine alla finestra.")
    hatch_cap_half_width = (
        loader["hatch_top_pocket_width"] / 2.0
        - loader["hatch_clearance_per_side"]
    )
    if loader_screw_x + loader_head_radius > (
        hatch_cap_half_width
        - loader["minimum_printed_wall"]
    ):
        raise RuntimeError("Le svasature del coperchio culatta sono troppo vicine al bordo.")
    if loader_screw_x + loader_boss_radius > (
        loader["hatch_top_pocket_width"] / 2.0
        - loader["minimum_printed_wall"]
    ):
        raise RuntimeError("I boss M2.5 non appoggiano abbastanza sul rinforzo locale.")

    parameter_specs = (
        ("cop_lunghezza", cover["outer_length"], "Ingombro coperchio"),
        ("cop_larghezza", cover["outer_width"], "Ingombro coperchio"),
        ("cop_parete_altezza", cover["wall_height"], "Quota locale del tetto removibile"),
        ("cop_tetto_spessore", cover["roof_thickness"], "Coperchio elettronica"),
        (
            "cop_boss_M3_diametro",
            data["base_standoffs"]["outer_diameter"],
            "Accesso vite M3 dal tetto alle colonnine",
        ),
        (
            "cop_canale_fondo_raggio_interno",
            roof_support["channel_floor_inner_radius"],
            "Fondo liscio pista cavi tipo clock-spring",
        ),
        (
            "cop_canale_fondo_raggio_esterno",
            roof_support["channel_floor_outer_radius"],
            "Fondo liscio pista cavi tipo clock-spring",
        ),
        (
            "cop_canale_fondo_quota",
            roof_support["channel_floor_bottom_z"],
            "Quota locale fondo pista cavi",
        ),
        (
            "cop_canale_fondo_spessore",
            roof_support["channel_floor_thickness"],
            "Fondo strutturale pista cavi",
        ),
        (
            "cop_canale_parete_spessore",
            roof_support["channel_wall_thickness"],
            "Pareti lisce pista cavi",
        ),
        (
            "cop_canale_altezza_libera",
            roof_support["channel_clearance_height"],
            "Altezza libera pista cavi",
        ),
        ("stepper_corpo_diametro", stepper["body_diameter"], "Riferimento stepper"),
        ("stepper_corpo_altezza", stepper["body_height"], "Riferimento stepper"),
        ("stepper_albero_diametro", stepper["shaft_diameter"], "Riferimento stepper"),
        ("stepper_albero_quota_tra_piatti", stepper["shaft_flat_to_flat"], "Profilo doppia-D confermato"),
        ("stepper_albero_lunghezza", stepper["shaft_length"], "Riferimento stepper"),
        ("stepper_interasse_fori", stepper["mounting_hole_spacing"], "Fissaggio stepper"),
        ("stepper_foro_fissaggio", stepper["mounting_hole_diameter"], "Fissaggio stepper"),
        ("stepper_svasatura_M4_diametro", stepper["mounting_countersink_diameter"], "Testa svasata a filo"),
        ("stepper_svasatura_M4_profondita", stepper["mounting_countersink_depth"], "Testa svasata a filo"),
        ("torre_base_diametro", rotating["diameter"], "Adattatore rotante"),
        ("torre_base_spessore", rotating["thickness"], "Adattatore rotante"),
        ("torre_sede_D_diametro", rotating["shaft_bore_diameter"], "Mozzo D stepper"),
        ("torre_sede_D_quota_tra_piatti", rotating["shaft_bore_flat_to_flat"], "Mozzo doppia-D stepper"),
        ("torre_mozzo_accoppiamento_diametro", rotating["coupling_hub_outer_diameter"], "Mozzo inferiore nel tetto"),
        ("torre_mozzo_accoppiamento_altezza", rotating["coupling_hub_height_below_base"], "Impegno albero da 6 mm"),
        ("torre_mozzo_gioco_tetto", rotating["coupling_hub_roof_clearance_per_side"], "Gioco radiale per lato"),
        ("torre_rondella_assiale_DI", azimuth_support["thrust_washer_inner_diameter"], "Appoggio assiale esterno ai cavi"),
        ("torre_rondella_assiale_DE", azimuth_support["thrust_washer_outer_diameter"], "Appoggio assiale esterno ai cavi"),
        ("torre_rondella_assiale_spessore", azimuth_support["thrust_washer_thickness"], "Appoggio assiale esterno ai cavi"),
        ("torre_rondella_sede_profondita", azimuth_support["thrust_washer_seat_depth"], "Localizzazione rondella"),
        ("torre_rondella_sede_gioco", azimuth_support["thrust_washer_seat_radial_clearance_per_side"], "Gioco per lato sede rondella"),
        ("torre_guida_fissa_RI", azimuth_support["fixed_guide_inner_radius"], "Centraggio radiale"),
        ("torre_guida_fissa_RE", azimuth_support["fixed_guide_outer_radius"], "Centraggio radiale"),
        ("torre_guida_fissa_altezza", azimuth_support["fixed_guide_height"], "Centraggio radiale"),
        ("torre_gola_gioco_radiale", azimuth_support["rotating_groove_radial_clearance_per_side"], "Gioco per lato"),
        ("torre_gola_profondita", azimuth_support["rotating_groove_depth"], "Guida rotante"),
        ("torre_fermaglio_gioco_verticale", azimuth_support["anti_lift_vertical_clearance"], "Anti-sollevamento"),
        ("torre_fermaglio_sovrapposizione", azimuth_support["anti_lift_overlap"], "Anti-sollevamento"),
        ("torre_fermaglio_foro_M3", azimuth_support["anti_lift_screw_hole_diameter"], "Fermagli removibili"),
        ("torre_fermaglio_spallamento_altezza", azimuth_support["anti_lift_key_height"], "Antirotazione fermagli"),
        ("torre_fermaglio_spallamento_larghezza", azimuth_support["anti_lift_key_width"], "Antirotazione fermagli"),
        ("torre_distanziale_telaio_altezza", azimuth_support["upper_frame_standoff_height"], "Evita collisione con fermagli"),
        ("torre_distanziale_telaio_diametro", azimuth_support["upper_frame_standoff_diameter"], "Quattro appoggi M3"),
        ("torre_fissa_larghezza", frame["width"], "Parte fissa torretta"),
        ("torre_fissa_lunghezza", frame["length"], "Parte fissa torretta"),
        ("torre_fissa_altezza", frame["height"], "Parte fissa torretta"),
        ("torre_parete_spessore", frame["wall_thickness"], "Parte fissa torretta"),
        ("torre_perno_quota", frame["pivot_above_base_top"], "Asse elevazione"),
        ("servo_corpo_lunghezza", servo["body_length"], "TowerPro SG90"),
        ("servo_corpo_larghezza", servo["body_width"], "TowerPro SG90"),
        ("servo_corpo_altezza", servo["body_height"], "TowerPro SG90"),
        ("servo_ingombro_con_uscita", servo["overall_height_with_output"], "TowerPro SG90"),
        ("servo_alette_lunghezza_totale", servo["mounting_flange_overall_length"], "TowerPro SG90"),
        ("servo_aletta_sporgenza", servo["mounting_ear_projection_nominal"], "Quota utente circa 5 mm"),
        ("servo_aletta_spessore", servo["mounting_ear_thickness"], "Quota utente 2 mm"),
        ("servo_aletta_foro_M2_5", servo["mounting_ear_hole_diameter"], "M2.5 provata sul pezzo"),
        ("servo_aletta_asola_telaio_lunghezza", servo["mounting_wall_slot_length"], "Registrazione lungo Y"),
        ("servo_aletta_asola_telaio_larghezza", servo["mounting_wall_slot_width"], "Passaggio M2.5 con gioco"),
        ("servo_aletta_parete_minima", servo["mounting_wall_min_web"], "Tra asola e finestra corpo"),
        ("servo_asse_da_estremita", servo["shaft_center_from_rear_body_end"], "TowerPro SG90"),
        ("servo_albero_sporgenza", servo["shaft_protrusion"], "TowerPro SG90"),
        ("servo_albero_diametro_riferimento", servo["drive_shaft_diameter"], "Solo inviluppo uscita SG90"),
        ("servo_cornetto_span_riferimento", servo["horn_reference_span"], "Cornetto reale usato come dima"),
        ("servo_cornetto_spessore_riferimento", servo["horn_reference_thickness"], "Quota visiva provvisoria"),
        ("servo_adattatore_cornetto_diametro", servo["horn_adapter_disc_diameter"], "Disco pieno senza interassi inventati"),
        ("servo_adattatore_cornetto_spessore", servo["horn_adapter_disc_thickness"], "Impegno viti appuntite"),
        ("servo_adattatore_accesso_vite_centrale", servo["horn_adapter_center_access_diameter"], "Accesso alla vite originale"),
        ("servo_adattatore_asola_regolazione", servo["horn_adapter_adjustment_slot_length"], "Registrazione assiale"),
        ("servo_gioco_inserimento", servo["fit_clearance_per_side"], "Slitta servo"),
        ("servo_supporto_parete", servo["holder_wall_thickness"], "Slitta servo"),
        ("servo_supporto_ripiano", servo["holder_shelf_thickness"], "Slitta servo"),
        ("servo_carter_foro_M2_5", servo["carter_screw_clearance_hole_diameter"], "Carter removibile"),
        ("servo_carter_preforo_M2_5", servo["carter_screw_pilot_hole_diameter"], "Supporto carter"),
        ("servo_cavo_larghezza", cable["servo_cable_profile_width"], "Cavo piatto SG90"),
        ("servo_cavo_spessore", cable["servo_cable_profile_thickness"], "Cavo piatto SG90"),
        ("servo_uscita_cavo_larghezza", cable["servo_holder_exit_notch_width"], "Slitta SG90"),
        ("servo_uscita_cavo_profondita", cable["servo_holder_exit_notch_depth"], "Slitta SG90"),
        ("servo_connettore_larghezza", cable["servo_connector_width"], "Connettore SG90"),
        ("servo_connettore_spessore", cable["servo_connector_thickness"], "Connettore SG90"),
        ("passaggio_comune_larghezza", cable["common_connector_passage_width"], "Passaggio connettori SG90"),
        ("passaggio_comune_lunghezza", cable["common_connector_passage_length"], "Passaggio connettori SG90"),
        ("passaggio_arco_raggio", cable["azimuth_arc_mean_radius"], "Guida cavi azimut"),
        ("passaggio_arco_larghezza", cable["azimuth_arc_radial_width"], "Guida cavi azimut"),
        ("ansa_azimut_lunghezza_libera", cable["azimuth_free_bundle_length"], "Fascio ordinato nel canale"),
        ("asola_fascetta_cavi_lunghezza", cable["cable_tie_slot_length"], "Fermacavi torretta"),
        ("asola_fascetta_cavi_larghezza", cable["cable_tie_slot_width"], "Fermacavi torretta"),
        ("asola_fascetta_cavi_interasse", cable["cable_tie_pair_spacing"], "Fermacavi torretta"),
        ("asola_fascetta_cannone_mobile_interasse", cable["mobile_cable_tie_pair_spacing"], "Ancoraggio ansa elevazione"),
        ("fermacavo_fisso_inferiore_larghezza", cable["fixed_lower_anchor_pad_width"], "Scarico trazione sotto uscita"),
        ("fermacavo_fisso_inferiore_lunghezza", cable["fixed_lower_anchor_pad_length"], "Scarico trazione sotto uscita"),
        ("fermacavo_fisso_inferiore_spessore", cable["fixed_lower_anchor_pad_thickness"], "Scarico trazione sotto uscita"),
        ("fermacavo_fisso_asole_offset_x", cable["fixed_lower_anchor_slot_offset_x"], "Sposta le asole fuori dal bordo anulare"),
        ("fermacavo_fisso_ponte_larghezza", cable["fixed_lower_anchor_bridge_width"], "Ponte strutturale verso il fondo anulare"),
        ("fermacavo_fisso_ponte_lunghezza", cable["fixed_lower_anchor_bridge_length"], "Ponte strutturale verso il fondo anulare"),
        ("cannone_connettore_larghezza", cable["cannon_connector_width"], "Connettore cannone"),
        ("cannone_connettore_spessore", cable["cannon_connector_thickness"], "Connettore cannone"),
        ("cannone_passaggio_mobile_larghezza", cable["cannon_mobile_passage_width"], "Passaggio sotto culla"),
        ("cannone_passaggio_mobile_lunghezza", cable["cannon_mobile_passage_length"], "Passaggio sotto culla"),
        ("pcb_cannone_lunghezza", firing["pcb_length"], "PCB mobile cannone"),
        ("pcb_cannone_larghezza", firing["pcb_width"], "PCB mobile cannone"),
        ("pcb_cannone_spessore", firing["pcb_thickness"], "PCB mobile cannone"),
        ("pcb_cannone_foro", firing["mounting_hole_diameter"], "Fori PCB cannone"),
        ("pcb_cannone_foro_bordo_x", firing["mounting_hole_edge_inset_x"], "Fori PCB cannone"),
        ("pcb_cannone_foro_bordo_y", firing["mounting_hole_edge_inset_y"], "Fori PCB cannone"),
        ("solenoide_diametro", firing["cannon_outer_diameter_at_solenoid"], "Zona solenoide"),
        ("solenoide_lunghezza", firing["solenoid_length"], "Zona solenoide"),
        ("canna_diametro_esterno", firing["barrel_outer_diameter"], "Canna tubolare"),
        ("canna_diametro_interno", firing["barrel_inner_diameter"], "Canna tubolare"),
        ("canna_parete", firing["barrel_wall_thickness"], "Canna tubolare"),
        ("canna_sporgenza", firing["barrel_protrusion_from_cannon_outlet"], "Canna tubolare"),
        ("modulo_cannone_altezza", firing["overall_height_from_pcb_bottom"], "Modulo mobile"),
        ("culatta_proiettile_diametro_max_provvisorio", loader["provisional_max_projectile_diameter"], "Solo proiettile morbido e inerte"),
        ("culatta_proiettile_lunghezza_max_provvisoria", loader["provisional_max_projectile_length"], "Ingombro di caricamento da verificare"),
        ("culatta_guida_diametro_esterno", loader["guide_outer_diameter"], "Invito interno coassiale"),
        ("culatta_guida_diametro_interno", loader["guide_inner_diameter"], "Invito interno coassiale"),
        ("culatta_guida_lunghezza", loader["guide_length"], "Invito interno coassiale"),
        ("culatta_finestra_posteriore_larghezza", loader["rear_window_width"], "Apertura a L removibile"),
        ("culatta_asola_tetto_lunghezza", loader["roof_slot_length"], "Apertura a L removibile"),
        ("culatta_coperchio_larghezza", loader["hatch_top_pocket_width"], "Coperchio a filo removibile"),
        ("culatta_coperchio_lunghezza", loader["hatch_top_pocket_length"], "Coperchio a filo removibile"),
        ("culatta_tasca_profondita", loader["hatch_top_pocket_depth"], "Alloggiamento coperchio removibile"),
        ("culatta_coperchio_spessore", loader["hatch_top_plate_thickness"], "Coperchio a filo removibile"),
        ("culatta_coperchio_gioco_verticale", loader["hatch_vertical_clearance"], "Coperchio leggermente ribassato"),
        ("culatta_rinforzo_locale_spessore", loader["hatch_local_reinforcement_thickness"], "Rinforzo a U sotto la tasca"),
        ("culatta_interasse_M2_5", loader["mounting_hole_spacing"], "Due viti accessibili dall'alto"),
        ("culatta_foro_M2_5", loader["clearance_hole_diameter"], "Coperchio removibile"),
        ("culatta_preforo_M2_5", loader["pilot_hole_diameter"], "Boss sotto il tetto"),
    )
    for name, value, comment in parameter_specs:
        _add_user_parameter(design, name, value, "mm", comment)
    _add_user_parameter(
        design,
        "cannone_elevazione_min",
        cannon["elevation_min_deg"],
        "deg",
        "Limite proposto asse elevazione",
    )
    _add_user_parameter(
        design,
        "cannone_elevazione_max",
        cannon["elevation_max_deg"],
        "deg",
        "Limite proposto asse elevazione",
    )
    _add_user_parameter(
        design,
        "passaggio_arco_angolo_iniziale",
        cable["azimuth_arc_start_deg"],
        "deg",
        "Inizio guida cavi di azimut",
    )
    _add_user_parameter(
        design,
        "passaggio_arco_corsa",
        cable["azimuth_arc_sweep_deg"],
        "deg",
        "Corsa totale guida cavi di azimut",
    )
    _add_user_parameter(
        design,
        "torretta_azimut_min",
        -cable["azimuth_rotation_range_deg"] / 2.0,
        "deg",
        "Limite software e giunto Fusion",
    )
    _add_user_parameter(
        design,
        "torretta_azimut_max",
        cable["azimuth_rotation_range_deg"] / 2.0,
        "deg",
        "Limite software e giunto Fusion",
    )

    cover_total_height = cover["wall_height"] + cover["roof_thickness"]
    washer_bottom = (
        cover_total_height - azimuth_support["thrust_washer_seat_depth"]
    )
    adapter_bottom = (
        washer_bottom + azimuth_support["thrust_washer_thickness"]
    )
    adapter_top = adapter_bottom + rotating["thickness"]
    fixed_base_bottom = (
        adapter_top + azimuth_support["upper_frame_standoff_height"]
    )
    fixed_base_top = fixed_base_bottom + frame["base_thickness"]
    pivot_z = fixed_base_top + frame["pivot_above_base_top"]

    # 01 - Tetto removibile senza pareti duplicate. Quattro boss M3 scendono
    # fino al piano superiore e permettono il serraggio dall'alto.
    cover_occ, cover_component = _new_component_occurrence(
        root, "01_Tetto_elettronica_removibile"
    )
    # Il tetto e il riferimento fisso della cinematica: lo blocchiamo subito,
    # prima di creare qualunque giunto, cosi anche un ricalcolo interrotto non
    # puo far scegliere a Fusion il gruppo inferiore come parte mobile.
    cover_occ.isGroundToParent = True
    if not cover_occ.isGroundToParent:
        raise RuntimeError("Fusion non ha fissato subito il tetto al sottoassieme padre.")
    cover_body, _ = _centered_rectangle_prism(
        cover_component,
        "Tetto_coperchio",
        cover["outer_width"],
        cover["outer_length"],
        "cop_tetto_spessore",
        "cop_parete_altezza",
    )
    cover_zero_plane = _offset_plane(cover_component, "0 mm")
    mounting_centers = (
        (-cover["mounting_hole_center_x"], -cover["mounting_hole_center_y"]),
        (cover["mounting_hole_center_x"], -cover["mounting_hole_center_y"]),
        (-cover["mounting_hole_center_x"], cover["mounting_hole_center_y"]),
        (cover["mounting_hole_center_x"], cover["mounting_hole_center_y"]),
    )
    for index, (center_x, center_y) in enumerate(mounting_centers, start=1):
        _cylinder_prism(
            cover_component,
            cover_zero_plane,
            f"Boss_verticale_M3_coperchio_{index:02d}",
            data["base_standoffs"]["outer_diameter"],
            center_x,
            center_y,
            f"{cover_total_height} mm",
            adsk.fusion.FeatureOperations.JoinFeatureOperation,
        )
        _cut_round_hole(
            cover_component,
            cover_zero_plane,
            cover["mounting_hole_diameter"],
            center_x,
            center_y,
            f"{cover_total_height} mm",
            f"Foro_M3_accessibile_dal_tetto_{index:02d}",
        )

    roof_plane = _offset_plane(cover_component, "cop_parete_altezza")
    roof_top_plane = _offset_plane(cover_component, f"{cover_total_height} mm")
    countersink_bottom_plane = _offset_plane(
        cover_component,
        f"{cover_total_height - stepper['mounting_countersink_depth']} mm",
    )
    shaft_roof_clearance = max(
        8.0,
        rotating["coupling_hub_outer_diameter"]
        + 2.0 * rotating["coupling_hub_roof_clearance_per_side"],
    )
    _cut_round_hole(
        cover_component,
        roof_plane,
        shaft_roof_clearance,
        0,
        0,
        "cop_tetto_spessore",
        "Passaggio_albero_stepper",
    )
    stepper_hole_x = stepper["mounting_hole_spacing"] / 2.0
    for side, center_x in (("Ovest", -stepper_hole_x), ("Est", stepper_hole_x)):
        _cut_round_hole(
            cover_component,
            roof_plane,
            stepper["mounting_hole_diameter"],
            center_x,
            0,
            "cop_tetto_spessore",
            f"Foro_stepper_{side}",
        )
        _cut_countersink_frustum(
            cover_component,
            countersink_bottom_plane,
            roof_top_plane,
            stepper["mounting_hole_diameter"],
            stepper["mounting_countersink_diameter"],
            center_x,
            0,
            f"Svasatura_90_gradi_stepper_{side}",
        )
    anti_lift_screw_radius = azimuth_support["anti_lift_screw_radius"]
    anti_lift_screw_centers = (
        ("Est", anti_lift_screw_radius, 0.0),
        ("Ovest", -anti_lift_screw_radius, 0.0),
        ("Nord", 0.0, anti_lift_screw_radius),
        ("Sud", 0.0, -anti_lift_screw_radius),
    )
    for side, center_x, center_y in anti_lift_screw_centers:
        _cut_round_hole(
            cover_component,
            roof_plane,
            azimuth_support["anti_lift_screw_hole_diameter"],
            center_x,
            center_y,
            "cop_tetto_spessore",
            f"Foro_M3_fermaglio_anti_sollevamento_{side}",
        )
        _cut_hex_pocket(
            cover_component,
            roof_plane,
            azimuth_support["anti_lift_nut_across_flats"],
            center_x,
            center_y,
            f"{azimuth_support['anti_lift_nut_trap_depth']} mm",
            f"Sede_dado_M3_fermaglio_{side}",
        )
    # Canale anulare tipo clock-spring. Le vecchie quattro razze attraversavano
    # la pista anulare e potevano agganciare l'ansa durante la corsa -180/+180.
    # Il fondo e le due pareti formano ora una superficie continua: la struttura
    # resta un unico corpo, mentre nel volume dei cavi non sporge alcun rinforzo.
    channel_floor_bottom = roof_support["channel_floor_bottom_z"]
    channel_floor_top = (
        channel_floor_bottom + roof_support["channel_floor_thickness"]
    )
    modeling_overlap = 0.2
    channel_wall_plane = _offset_plane(
        cover_component, f"{channel_floor_top - modeling_overlap} mm"
    )
    channel_wall_height = (
        cover["wall_height"]
        - channel_floor_top
        + 2.0 * modeling_overlap
    )
    _annular_prism(
        cover_component,
        channel_wall_plane,
        "Parete_interna_liscia_canale_cavi",
        arc_inner_radius - roof_support["channel_wall_thickness"],
        arc_inner_radius,
        f"{channel_wall_height} mm",
        adsk.fusion.FeatureOperations.JoinFeatureOperation,
    )
    _annular_prism(
        cover_component,
        channel_wall_plane,
        "Parete_esterna_liscia_canale_cavi",
        arc_outer_radius,
        arc_outer_radius + roof_support["channel_wall_thickness"],
        f"{channel_wall_height} mm",
        adsk.fusion.FeatureOperations.JoinFeatureOperation,
    )
    channel_floor_plane = _offset_plane(
        cover_component, f"{channel_floor_bottom} mm"
    )
    _annular_prism(
        cover_component,
        channel_floor_plane,
        "Fondo_anulare_continuo_canale_cavi",
        roof_support["channel_floor_inner_radius"],
        roof_support["channel_floor_outer_radius"],
        "cop_canale_fondo_spessore",
        adsk.fusion.FeatureOperations.JoinFeatureOperation,
    )
    _cut_rotated_rectangle(
        cover_component,
        channel_floor_plane,
        cable["common_connector_passage_width"],
        cable["common_connector_passage_length"],
        cable["azimuth_arc_mean_radius"],
        cable["rotating_passage_center_angle_deg"],
        "cop_canale_fondo_spessore",
        "Uscita_fissa_9x7_canale_cavi_verso_vano_elettronica",
    )
    # Scarico di trazione realmente fisso, sotto l'uscita: impedisce che il
    # movimento richiami cavo dall'Arduino o trasferisca sforzo ai connettori.
    lower_anchor_plane = _offset_plane(
        cover_component,
        f"{channel_floor_bottom - cable['fixed_lower_anchor_pad_thickness']} mm",
    )
    _rectangle_prism_at(
        cover_component,
        lower_anchor_plane,
        "Piastrina_fermacavo_fissa_sotto_uscita",
        cable["fixed_lower_anchor_pad_width"],
        cable["fixed_lower_anchor_pad_length"],
        cable["fixed_lower_anchor_pad_center_x"],
        cable["fixed_lower_anchor_pad_center_y"],
        f"{cable['fixed_lower_anchor_pad_thickness'] + modeling_overlap} mm",
        adsk.fusion.FeatureOperations.JoinFeatureOperation,
    )
    # Un ponte largo collega la piastrina al fondo anulare con una sezione
    # realmente stampabile. Senza questo ponte il primo legamento vicino a r40
    # sarebbe affidato a una linguetta troppo sottile per un ugello da 0,4 mm.
    _rectangle_prism_at(
        cover_component,
        lower_anchor_plane,
        "Ponte_strutturale_fermacavo_fisso",
        cable["fixed_lower_anchor_bridge_width"],
        cable["fixed_lower_anchor_bridge_length"],
        cable["fixed_lower_anchor_bridge_center_x"],
        cable["fixed_lower_anchor_bridge_center_y"],
        f"{cable['fixed_lower_anchor_pad_thickness'] + modeling_overlap} mm",
        adsk.fusion.FeatureOperations.JoinFeatureOperation,
    )
    for pair_index, y_sign in enumerate((-1.0, 1.0), start=1):
        _cut_rectangle(
            cover_component,
            lower_anchor_plane,
            cable["cable_tie_slot_length"],
            cable["cable_tie_slot_width"],
            cable["fixed_lower_anchor_pad_center_x"]
            + cable["fixed_lower_anchor_slot_offset_x"],
            cable["fixed_lower_anchor_pad_center_y"]
            + y_sign * cable["cable_tie_pair_spacing"] / 2.0,
            f"{cable['fixed_lower_anchor_pad_thickness'] + modeling_overlap} mm",
            f"Asola_fermacavo_fissa_inferiore_{pair_index:02d}",
        )
    if full_annular_path:
        _cut_annular_ring(
            cover_component,
            roof_plane,
            cable["azimuth_arc_mean_radius"],
            cable["azimuth_arc_radial_width"],
            "cop_tetto_spessore",
            "Guida_anulare_cavi_azimut_meno180_piu180",
        )
    else:
        _cut_annular_sector(
            cover_component,
            roof_plane,
            cable["azimuth_arc_mean_radius"],
            cable["azimuth_arc_radial_width"],
            cable["azimuth_arc_start_deg"],
            cable["azimuth_arc_sweep_deg"],
            "cop_tetto_spessore",
            "Guida_arcuata_cavi_azimut",
        )

    # La rondella entra in una sede anulare superficiale: non può traslare
    # durante montaggio e rotazione, ma resta sostituibile senza viti.
    washer_seat_plane = _offset_plane(
        cover_component, f"{washer_bottom} mm"
    )
    _cut_annular_ring(
        cover_component,
        washer_seat_plane,
        (washer_inner_radius + washer_outer_radius) / 2.0,
        (washer_outer_radius - washer_inner_radius)
        + 2.0 * washer_seat_clearance,
        f"{azimuth_support['thrust_washer_seat_depth']} mm",
        "Sede_ribassata_rondella_assiale",
    )

    # Labbro fisso di centraggio, esterno alla pista r23.5-r32.5. Entra con
    # gioco nella gola inferiore della base rotante e non porta il peso.
    guide_join_overlap = 0.5
    guide_plane = _offset_plane(
        cover_component, f"{cover_total_height - guide_join_overlap} mm"
    )
    guide_feature = _annular_prism(
        cover_component,
        guide_plane,
        "Labbro_fisso_centraggio_radiale_torretta",
        azimuth_support["fixed_guide_inner_radius"],
        azimuth_support["fixed_guide_outer_radius"],
        f"{azimuth_support['fixed_guide_height'] + guide_join_overlap} mm",
    )
    expected_guide_top_z = cover_total_height + azimuth_support["fixed_guide_height"]
    guide_body = guide_feature.bodies.item(0)
    separate_guide_top_z = guide_body.boundingBox.maxPoint.z * 10.0
    if abs(separate_guide_top_z - expected_guide_top_z) > 0.05:
        raise RuntimeError(
            "Il labbro di centraggio non raggiunge l'altezza prevista: "
            f"atteso {expected_guide_top_z:.2f} mm, ottenuto {separate_guide_top_z:.2f} mm."
        )
    _combine_join(
        cover_component,
        cover_body,
        (guide_body,),
        "Unione_labbro_fisso_al_tetto",
    )
    if cover_component.bRepBodies.count != 1:
        raise RuntimeError("Tetto e labbro fisso devono risultare in un solo corpo stampabile.")
    # Due spallamenti per fermaglio impediscono che la singola vite M3 diventi
    # un perno di rotazione. Restano fuori dal disco D100 e non lo sfiorano.
    key_plane = _offset_plane(
        cover_component, f"{cover_total_height - modeling_overlap} mm"
    )
    foot_inner = azimuth_support["anti_lift_foot_inner_radius"]
    foot_outer = azimuth_support["anti_lift_foot_outer_radius"]
    foot_center = (foot_inner + foot_outer) / 2.0
    foot_radial_length = foot_outer - foot_inner
    tangent_width = azimuth_support["anti_lift_tangential_width"]
    key_width = azimuth_support["anti_lift_key_width"]
    key_offset = (
        tangent_width / 2.0
        + azimuth_support["anti_lift_key_side_clearance"]
        + key_width / 2.0
    )
    for side, axis, sign in (
        ("Est", "x", 1.0),
        ("Ovest", "x", -1.0),
        ("Nord", "y", 1.0),
        ("Sud", "y", -1.0),
    ):
        for key_index, tangent_sign in enumerate((-1.0, 1.0), start=1):
            if axis == "x":
                key_body_width, key_body_length = foot_radial_length, key_width
                key_x, key_y = sign * foot_center, tangent_sign * key_offset
            else:
                key_body_width, key_body_length = key_width, foot_radial_length
                key_x, key_y = tangent_sign * key_offset, sign * foot_center
            _rectangle_prism_at(
                cover_component,
                key_plane,
                f"Spallamento_antirotazione_{side}_{key_index:02d}",
                key_body_width,
                key_body_length,
                key_x,
                key_y,
                f"{azimuth_support['anti_lift_key_height'] + modeling_overlap} mm",
                adsk.fusion.FeatureOperations.JoinFeatureOperation,
            )
    if cover_component.bRepBodies.count != 1:
        raise RuntimeError(
            "Il tetto removibile deve risultare in un unico corpo con canale cavi e boss M3."
        )
    cover_component.bRepBodies.item(0).name = (
        "Tetto_fisso_canale_cavi_guida_radiale_supporto_stepper_boss_M3"
    )

    # Rondella assiale sostituibile. Resta fissa al tetto e porta il peso della
    # torretta a raggio elevato; preferibile PTFE/POM, stampabile per prototipo.
    thrust_occ, thrust_component = _new_component_occurrence(
        root, "02A_Rondella_assiale_torretta_sostituibile"
    )
    thrust_plane = _offset_plane(thrust_component, f"{washer_bottom} mm")
    _annular_prism(
        thrust_component,
        thrust_plane,
        "Rondella_assiale_basso_attrito",
        washer_inner_radius,
        washer_outer_radius,
        f"{azimuth_support['thrust_washer_thickness']} mm",
    )
    thrust_component.bRepBodies.item(0).name = (
        "Rondella_assiale_DI76_DE94_spessore_0_8"
    )

    # 02 - Statore dello stepper fissato al tetto. L'albero viene modellato in
    # un componente distinto, così la simulazione non può ruotare il motore e
    # il tetto al posto della base D100.
    stepper_occ, stepper_component = _new_component_occurrence(
        root, "02_Stepper_28BYJ48_statore_fisso_riferimento"
    )
    stepper_body_bottom = cover["wall_height"] - stepper["body_height"]
    stepper_body_plane = _offset_plane(
        stepper_component, f"{stepper_body_bottom} mm"
    )
    _cylinder_prism(
        stepper_component,
        stepper_body_plane,
        "Corpo_stepper",
        stepper["body_diameter"],
        0,
        0,
        "stepper_corpo_altezza",
    )
    tab_plane = _offset_plane(
        stepper_component, f"{cover['wall_height'] - 3.0} mm"
    )
    _rectangle_prism_at(
        stepper_component,
        tab_plane,
        "Alette_fissaggio_stepper",
        stepper["overall_tab_width"],
        8,
        0,
        0,
        "3 mm",
        adsk.fusion.FeatureOperations.JoinFeatureOperation,
    )
    rotor_occ, rotor_component = _new_component_occurrence(
        root, "02B_Rotore_albero_28BYJ48_riferimento"
    )
    shaft_plane = _offset_plane(rotor_component, f"{cover['wall_height']} mm")
    _cylinder_prism(
        rotor_component,
        shaft_plane,
        "Albero_stepper",
        stepper["shaft_diameter"],
        0,
        0,
        "stepper_albero_lunghezza",
    )
    shaft_radius = stepper["shaft_diameter"] / 2.0
    shaft_half_flat = stepper["shaft_flat_to_flat"] / 2.0
    shaft_flat_cut_width = shaft_radius - shaft_half_flat
    _cut_rectangle(
        rotor_component,
        shaft_plane,
        shaft_flat_cut_width,
        stepper["shaft_diameter"] + 0.4,
        -(shaft_radius + shaft_half_flat) / 2.0,
        0,
        "stepper_albero_lunghezza",
        "Piatto_sinistro_albero_stepper",
    )
    _cut_rectangle(
        rotor_component,
        shaft_plane,
        shaft_flat_cut_width,
        stepper["shaft_diameter"] + 0.4,
        (shaft_radius + shaft_half_flat) / 2.0,
        0,
        "stepper_albero_lunghezza",
        "Piatto_destro_albero_stepper",
    )

    # 03 - Base rotante sostenuta dalla rondella esterna. Il foro centrale viene
    # richiuso sui due lati opposti dopo il taglio circolare, ottenendo una
    # vera sede doppia-D coerente con l'albero reale del 28BYJ-48.
    adapter_occ, adapter_component = _new_component_occurrence(
        root, "03_Base_rotante_D100_sede_D_stepper"
    )
    adapter_plane = _offset_plane(adapter_component, f"{adapter_bottom} mm")
    _cylinder_prism(
        adapter_component,
        adapter_plane,
        "Piastra_base_rotante_D100",
        rotating["diameter"],
        0,
        0,
        "torre_base_spessore",
    )
    coupling_hub_height = rotating["coupling_hub_height_below_base"]
    coupling_hub_bottom = adapter_bottom - coupling_hub_height
    coupling_hub_plane = _offset_plane(
        adapter_component, f"{coupling_hub_bottom} mm"
    )
    _cylinder_prism(
        adapter_component,
        coupling_hub_plane,
        "Mozzo_inferiore_accoppiamento_stepper",
        rotating["coupling_hub_outer_diameter"],
        0,
        0,
        f"{coupling_hub_height + 0.2} mm",
        adsk.fusion.FeatureOperations.JoinFeatureOperation,
    )
    coupling_bore_depth = coupling_hub_height + rotating["thickness"] + 0.2
    _cut_round_hole(
        adapter_component,
        coupling_hub_plane,
        rotating["shaft_bore_diameter"],
        0,
        0,
        f"{coupling_bore_depth} mm",
        "Preforo_circolare_sede_D_stepper",
    )
    bore_radius = rotating["shaft_bore_diameter"] / 2.0
    bore_half_flat = rotating["shaft_bore_flat_to_flat"] / 2.0
    bore_fill_width = bore_radius - bore_half_flat
    if bore_fill_width <= 0:
        raise RuntimeError("Impossibile costruire i lati piatti della sede doppia-D.")
    _rectangle_prism_at(
        adapter_component,
        adapter_plane,
        "Riempimento_lato_sinistro_sede_doppia_D",
        bore_fill_width,
        rotating["shaft_bore_diameter"] + 0.4,
        -(bore_radius + bore_half_flat) / 2.0,
        0,
        f"{coupling_bore_depth} mm",
        adsk.fusion.FeatureOperations.JoinFeatureOperation,
    )
    _rectangle_prism_at(
        adapter_component,
        adapter_plane,
        "Riempimento_lato_destro_sede_doppia_D",
        bore_fill_width,
        rotating["shaft_bore_diameter"] + 0.4,
        (bore_radius + bore_half_flat) / 2.0,
        0,
        f"{coupling_bore_depth} mm",
        adsk.fusion.FeatureOperations.JoinFeatureOperation,
    )

    guide_groove_mean = (guide_groove_inner + guide_groove_outer) / 2.0
    guide_groove_width = guide_groove_outer - guide_groove_inner
    _cut_annular_ring(
        adapter_component,
        adapter_plane,
        guide_groove_mean,
        guide_groove_width,
        f"{azimuth_support['rotating_groove_depth']} mm",
        "Gola_inferiore_centraggio_radiale_con_gioco",
    )
    adapter_mounts = adapter_mount_centers
    adapter_nut_plane = _offset_plane(
        adapter_component,
        f"{adapter_top - rotating['nut_trap_depth']} mm",
    )
    for index, (center_x, center_y) in enumerate(adapter_mounts, start=1):
        _cut_round_hole(
            adapter_component,
            adapter_plane,
            rotating["mounting_hole_diameter"],
            center_x,
            center_y,
            "torre_base_spessore",
            f"Foro_M3_adattatore_{index:02d}",
        )
        _cut_hex_pocket(
            adapter_component,
            adapter_nut_plane,
            rotating["nut_across_flats"],
            center_x,
            center_y,
            f"{rotating['nut_trap_depth']} mm",
            f"Sede_dado_M3_adattatore_{index:02d}",
        )
    _cut_rotated_rectangle(
        adapter_component,
        adapter_plane,
        cable["common_connector_passage_width"],
        cable["common_connector_passage_length"],
        cable["azimuth_arc_mean_radius"],
        cable["rotating_passage_center_angle_deg"],
        "torre_base_spessore",
        "Passaggio_9x7_comune_servi_cannone_adattatore",
    )
    if adapter_component.bRepBodies.count != 1:
        raise RuntimeError("La base rotante D100 deve risultare in un solo corpo.")
    adapter_component.bRepBodies.item(0).name = (
        "Base_rotante_D100_sede_D_gola_guida_passaggio_cavi"
    )

    # Quattro fermagli removibili impediscono il sollevamento e il ribaltamento
    # del disco, ma la linguetta superiore lascia 0.4 mm e non lo serra.
    anti_lift_clip_occurrences = []
    foot_inner = azimuth_support["anti_lift_foot_inner_radius"]
    foot_outer = azimuth_support["anti_lift_foot_outer_radius"]
    foot_center = (foot_inner + foot_outer) / 2.0
    foot_radial_length = foot_outer - foot_inner
    post_inner = azimuth_support["anti_lift_post_inner_radius"]
    post_outer = azimuth_support["anti_lift_post_outer_radius"]
    post_center = (post_inner + post_outer) / 2.0
    post_radial_length = post_outer - post_inner
    cap_inner = rotating["diameter"] / 2.0 - azimuth_support["anti_lift_overlap"]
    cap_outer = azimuth_support["anti_lift_cap_outer_radius"]
    cap_center = (cap_inner + cap_outer) / 2.0
    cap_radial_length = cap_outer - cap_inner
    cap_bottom = adapter_top + azimuth_support["anti_lift_vertical_clearance"]
    post_bottom = cover_total_height + azimuth_support["anti_lift_foot_thickness"]
    post_height = cap_bottom - post_bottom
    if post_height <= 0 or cap_radial_length <= 0:
        raise RuntimeError("Quote fermagli anti-sollevamento non assemblabili.")

    clip_specs = (
        ("Est", "x", 1.0),
        ("Ovest", "x", -1.0),
        ("Nord", "y", 1.0),
        ("Sud", "y", -1.0),
    )
    for side, axis, sign in clip_specs:
        clip_occ, clip_component = _new_component_occurrence(
            root, f"03A_Fermaglio_anti_sollevamento_{side}_M3"
        )
        clip_foot_plane = _offset_plane(
            clip_component, f"{cover_total_height} mm"
        )
        clip_post_plane = _offset_plane(clip_component, f"{post_bottom} mm")
        clip_cap_plane = _offset_plane(clip_component, f"{cap_bottom} mm")
        tangent_width = azimuth_support["anti_lift_tangential_width"]
        if axis == "x":
            foot_width, foot_length = foot_radial_length, tangent_width
            foot_x, foot_y = sign * foot_center, 0.0
            post_width, post_length = post_radial_length, tangent_width
            post_x, post_y = sign * post_center, 0.0
            cap_width, cap_length = cap_radial_length, tangent_width
            cap_x, cap_y = sign * cap_center, 0.0
            screw_x, screw_y = sign * anti_lift_screw_radius, 0.0
        else:
            foot_width, foot_length = tangent_width, foot_radial_length
            foot_x, foot_y = 0.0, sign * foot_center
            post_width, post_length = tangent_width, post_radial_length
            post_x, post_y = 0.0, sign * post_center
            cap_width, cap_length = tangent_width, cap_radial_length
            cap_x, cap_y = 0.0, sign * cap_center
            screw_x, screw_y = 0.0, sign * anti_lift_screw_radius
        _rectangle_prism_at(
            clip_component,
            clip_foot_plane,
            f"Piede_fermaglio_{side}",
            foot_width,
            foot_length,
            foot_x,
            foot_y,
            f"{azimuth_support['anti_lift_foot_thickness']} mm",
        )
        _rectangle_prism_at(
            clip_component,
            clip_post_plane,
            f"Montante_fermaglio_{side}",
            post_width,
            post_length,
            post_x,
            post_y,
            f"{post_height} mm",
            adsk.fusion.FeatureOperations.JoinFeatureOperation,
        )
        _rectangle_prism_at(
            clip_component,
            clip_cap_plane,
            f"Linguetta_fermaglio_{side}",
            cap_width,
            cap_length,
            cap_x,
            cap_y,
            f"{azimuth_support['anti_lift_cap_thickness']} mm",
            adsk.fusion.FeatureOperations.JoinFeatureOperation,
        )
        _cut_round_hole(
            clip_component,
            clip_foot_plane,
            azimuth_support["anti_lift_screw_hole_diameter"],
            screw_x,
            screw_y,
            f"{azimuth_support['anti_lift_foot_thickness']} mm",
            f"Foro_M3_fermaglio_{side}",
        )
        if clip_component.bRepBodies.count != 1:
            raise RuntimeError(f"Il fermaglio {side} deve essere un solo corpo.")
        anti_lift_clip_occurrences.append(clip_occ)

    # 04 - Parte fissa: ruota in azimut con lo stepper, ma i servo restano
    # solidali a questa struttura e comandano soltanto l'elevazione.
    fixed_occ, fixed_component = _new_component_occurrence(
        root, "04_Torretta_parte_fissa_azimut"
    )
    fixed_base_plane = _offset_plane(fixed_component, f"{fixed_base_bottom} mm")
    _rectangle_prism_at(
        fixed_component,
        fixed_base_plane,
        "Base_parte_fissa",
        frame["width"],
        frame["length"],
        0,
        0,
        f"{frame['base_thickness']} mm",
    )
    fixed_spacer_plane = _offset_plane(fixed_component, f"{adapter_top} mm")
    for index, (center_x, center_y) in enumerate(adapter_mounts, start=1):
        _cylinder_prism(
            fixed_component,
            fixed_spacer_plane,
            f"Distanziale_telaio_M3_{index:02d}",
            azimuth_support["upper_frame_standoff_diameter"],
            center_x,
            center_y,
            f"{azimuth_support['upper_frame_standoff_height'] + 0.2} mm",
            adsk.fusion.FeatureOperations.JoinFeatureOperation,
        )
        _cut_round_hole(
            fixed_component,
            fixed_spacer_plane,
            rotating["mounting_hole_diameter"],
            center_x,
            center_y,
            f"{azimuth_support['upper_frame_standoff_height'] + frame['base_thickness']} mm",
            f"Foro_M3_base_fissa_{index:02d}",
        )
    _cut_rotated_rectangle(
        fixed_component,
        fixed_base_plane,
        cable["common_connector_passage_width"],
        cable["common_connector_passage_length"],
        cable["azimuth_arc_mean_radius"],
        cable["rotating_passage_center_angle_deg"],
        f"{frame['base_thickness']} mm",
        "Passaggio_9x7_comune_servi_cannone_base_fissa",
    )

    # Tre coppie di asole per piccole fascette: SG90 sinistro, ansa cannone e
    # SG90 destro. Impediscono che la trazione arrivi ai connettori o alla pista.
    for anchor_name, anchor_x, anchor_y in fixed_anchor_specs:
        for pair_index, y_sign in enumerate((-1.0, 1.0), start=1):
            _cut_rectangle(
                fixed_component,
                fixed_base_plane,
                cable["cable_tie_slot_length"],
                cable["cable_tie_slot_width"],
                anchor_x,
                anchor_y
                + y_sign * cable["cable_tie_pair_spacing"] / 2.0,
                f"{frame['base_thickness']} mm",
                f"Asola_fermacavo_{anchor_name}_{pair_index:02d}",
            )

    frame_outer_x = frame["width"] / 2.0
    left_wall_x = -frame_outer_x
    right_wall_x = frame_outer_x - frame["wall_thickness"]
    left_inner_face_x = left_wall_x + frame["wall_thickness"]
    right_inner_face_x = right_wall_x
    wall_center_z = fixed_base_top + frame["height"] / 2.0

    # L'SG90 viene coricato: altezza del corpo lungo X, lunghezza lungo Y e
    # larghezza lungo Z. L'asse di uscita e quindi orizzontale e coassiale a X.
    servo_clearance = servo["fit_clearance_per_side"]
    servo_center_y = (
        servo["body_length"] / 2.0
        - servo["shaft_center_from_rear_body_end"]
    )
    servo_window_length = servo["body_length"] + 2.0 * servo_clearance
    servo_window_height = servo["body_width"] + 2.0 * servo_clearance
    servo_slot_length = (
        servo["mounting_flange_overall_length"] + 2.0 * servo_clearance
    )
    servo_ear_hole_centers_y = (
        servo_center_y - servo_ear_hole_offset_y,
        servo_center_y + servo_ear_hole_offset_y,
    )
    servo_window_min_y = servo_center_y - servo_window_length / 2.0
    servo_slot_outward_shift = (
        servo_ear_hole_centers_y[0]
        + servo["mounting_wall_slot_length"] / 2.0
        - servo_window_min_y
        + servo["mounting_wall_min_web"]
    )
    servo_slot_height = servo_window_height
    servo_cable_branch_top_z = pivot_z - servo_window_height / 2.0
    servo_cable_branch_height = (
        servo["holder_shelf_thickness"]
        + cable["servo_cable_profile_thickness"]
        + 2.0 * clearance
    )
    servo_cable_branch_center_z = (
        servo_cable_branch_top_z - servo_cable_branch_height / 2.0
    )

    if servo["shaft_center_from_rear_body_end"] >= servo["body_length"]:
        raise RuntimeError(
            "Quota asse SG90 incoerente: deve restare dentro la lunghezza del corpo"
        )
    if servo_window_height >= frame["height"]:
        raise RuntimeError("La finestra SG90 non entra nell'altezza della torretta")

    for side, plane_x in (("Sinistra", left_wall_x), ("Destra", right_wall_x)):
        plane_expression = f"{plane_x} mm"
        _vertical_rectangle_prism_x(
            fixed_component,
            f"Parete_fissa_{side}",
            plane_expression,
            frame["length"],
            frame["height"],
            0,
            wall_center_z,
            f"{frame['wall_thickness']} mm",
            adsk.fusion.FeatureOperations.JoinFeatureOperation,
        )
        _cut_vertical_rectangle_x(
            fixed_component,
            plane_expression,
            servo_window_length,
            servo_window_height,
            servo_center_y,
            pivot_z,
            f"{frame['wall_thickness']} mm",
            f"Finestra_inserimento_SG90_{side}",
        )
        _cut_vertical_rectangle_x(
            fixed_component,
            plane_expression,
            cable["servo_holder_exit_notch_width"],
            servo_cable_branch_height,
            servo_center_y,
            servo_cable_branch_center_z,
            f"{frame['wall_thickness']} mm",
            f"Diramazione_cavo_5x4_5_SG90_{side}",
        )
        for ear_index, ear_hole_y in enumerate(
            servo_ear_hole_centers_y, start=1
        ):
            outward_sign = -1.0 if ear_index == 1 else 1.0
            slot_center_y = (
                ear_hole_y + outward_sign * servo_slot_outward_shift
            )
            _cut_vertical_rectangle_x(
                fixed_component,
                plane_expression,
                servo["mounting_wall_slot_length"],
                servo["mounting_wall_slot_width"],
                slot_center_y,
                pivot_z,
                f"{frame['wall_thickness']} mm",
                f"Asola_M2_5_aletta_SG90_{side}_{ear_index:02d}",
            )

    # Slitte esterne integrate nella parte fissa. Il corpo entra dall'esterno,
    # attraversa la finestra e porta l'albero sul lato interno della parete.
    holder_wall = servo["holder_wall_thickness"]
    holder_shelf = servo["holder_shelf_thickness"]
    outside_body_depth = servo["body_height"] - frame["wall_thickness"]
    cage_depth = outside_body_depth + servo_clearance
    cage_overall_length = servo_slot_length + 2.0 * holder_wall
    bottom_shelf_z = pivot_z - servo_slot_height / 2.0 - holder_shelf
    top_shelf_z = pivot_z + servo_slot_height / 2.0
    left_cage_outer_x = -frame_outer_x - cage_depth
    right_cage_outer_x = frame_outer_x + cage_depth
    cage_specs = (
        ("Sinistra", left_cage_outer_x, -frame_outer_x - cage_depth / 2.0),
        ("Destra", frame_outer_x, frame_outer_x + cage_depth / 2.0),
    )
    rail_centers_y = (
        servo_center_y - servo_slot_length / 2.0 - holder_wall / 2.0,
        servo_center_y + servo_slot_length / 2.0 + holder_wall / 2.0,
    )
    for side, cage_plane_x, shelf_center_x in cage_specs:
        for shelf_name, shelf_z in (("Inferiore", bottom_shelf_z), ("Superiore", top_shelf_z)):
            shelf_plane = _offset_plane(fixed_component, f"{shelf_z} mm")
            _rectangle_prism_at(
                fixed_component,
                shelf_plane,
                f"Slitta_SG90_{side}_ripiano_{shelf_name}",
                cage_depth,
                cage_overall_length,
                shelf_center_x,
                servo_center_y,
                f"{holder_shelf} mm",
                adsk.fusion.FeatureOperations.JoinFeatureOperation,
            )
        notch_depth = cable["servo_holder_exit_notch_depth"]
        notch_outer_x = left_cage_outer_x if side == "Sinistra" else right_cage_outer_x
        notch_center_x = (
            notch_outer_x + notch_depth / 2.0
            if side == "Sinistra"
            else notch_outer_x - notch_depth / 2.0
        )
        notch_plane = _offset_plane(fixed_component, f"{bottom_shelf_z} mm")
        _cut_rectangle(
            fixed_component,
            notch_plane,
            notch_depth,
            cable["servo_holder_exit_notch_width"],
            notch_center_x,
            servo_center_y,
            f"{holder_shelf} mm",
            f"Uscita_cavo_5x2_SG90_{side}",
        )
        for rail_index, rail_center_y in enumerate(rail_centers_y, start=1):
            _vertical_rectangle_prism_x(
                fixed_component,
                f"Slitta_SG90_{side}_guida_{rail_index:02d}",
                f"{cage_plane_x} mm",
                holder_wall,
                servo_slot_height,
                rail_center_y,
                pivot_z,
                f"{cage_depth} mm",
                adsk.fusion.FeatureOperations.JoinFeatureOperation,
            )

        pilot_start_x = left_cage_outer_x if side == "Sinistra" else frame_outer_x
        for rail_index, rail_center_y in enumerate(rail_centers_y, start=1):
            _cut_round_hole_x(
                fixed_component,
                f"{pilot_start_x} mm",
                servo["carter_screw_pilot_hole_diameter"],
                rail_center_y,
                pivot_z,
                f"{cage_depth} mm",
                f"Preforo_M2_5_slitta_{side}_{rail_index:02d}",
            )

    # 05/06 - Corpi fissi SG90. Le alette reali da 2 mm appoggiano alle pareti
    # e vengono serrate con M2.5 nelle asole regolabili. Albero e cornetto non
    # sono fusi al corpo: appartengono alla catena mobile di elevazione.
    servo_occurrences = []
    servo_body_specs = (
        (
            "Sinistro",
            left_inner_face_x - servo["body_height"],
            left_wall_x - servo["mounting_ear_thickness"],
        ),
        ("Destro", right_inner_face_x, frame_outer_x),
    )
    for number, (side, body_start_x, flange_start_x) in enumerate(
        servo_body_specs,
        start=5,
    ):
        servo_occ, servo_component = _new_component_occurrence(
            root, f"{number:02d}_Servo_TowerPro_SG90_{side}_statore_riferimento"
        )
        _vertical_rectangle_prism_x(
            servo_component,
            f"Corpo_SG90_{side}",
            f"{body_start_x} mm",
            servo["body_length"],
            servo["body_width"],
            servo_center_y,
            pivot_z,
            "servo_corpo_altezza",
        )
        _vertical_rectangle_prism_x(
            servo_component,
            f"Alette_fissaggio_reali_SG90_{side}",
            f"{flange_start_x} mm",
            servo["mounting_flange_overall_length"],
            servo["body_width"],
            servo_center_y,
            pivot_z,
            f"{servo['mounting_ear_thickness']} mm",
            adsk.fusion.FeatureOperations.JoinFeatureOperation,
        )
        for ear_index, ear_hole_y in enumerate(
            servo_ear_hole_centers_y, start=1
        ):
            _cut_round_hole_x(
                servo_component,
                f"{flange_start_x} mm",
                servo["mounting_ear_hole_diameter"],
                ear_hole_y,
                pivot_z,
                f"{servo['mounting_ear_thickness']} mm",
                f"Foro_M2_5_aletta_reale_{side}_{ear_index:02d}",
            )
        servo_occurrences.append(servo_occ)

    # 09 - Culla mobile centrale. Non incorpora piu perni lisci inventati:
    # riceve invece due guance regolabili, ciascuna avvitata dal basso e
    # collegata al cornetto a croce originale del relativo SG90.
    mobile_occ, mobile_component = _new_component_occurrence(
        root, "09_Torretta_parte_mobile_elevazione"
    )
    mobile_width = (
        frame["width"]
        - 2.0 * frame["wall_thickness"]
        - 2.0 * frame["mobile_side_clearance"]
    )
    mobile_plate_plane = _offset_plane(
        mobile_component, f"{pivot_z - frame['mobile_plate_thickness'] / 2.0} mm"
    )
    _rectangle_prism_at(
        mobile_component,
        mobile_plate_plane,
        "Piastra_culla_mobile",
        mobile_width,
        frame["mobile_length"],
        0,
        15,
        f"{frame['mobile_plate_thickness']} mm",
    )
    pcb_center_y = 15.0
    mobile_rear_y = pcb_center_y - frame["mobile_length"] / 2.0
    pcb_rear_y = pcb_center_y - firing["pcb_length"] / 2.0
    cannon_cable_slot_center_y = (mobile_rear_y + pcb_rear_y) / 2.0
    _cut_rectangle(
        mobile_component,
        mobile_plate_plane,
        cable["cannon_mobile_passage_width"],
        cable["cannon_mobile_passage_length"],
        0,
        cannon_cable_slot_center_y,
        f"{frame['mobile_plate_thickness']} mm",
        "Passaggio_6x4_connettore_cannone_sotto_culla",
    )
    mobile_anchor_half_spacing = cable["mobile_cable_tie_pair_spacing"] / 2.0
    for anchor_index, anchor_x in enumerate(
        (-mobile_anchor_half_spacing, mobile_anchor_half_spacing), start=1
    ):
        _cut_rectangle(
            mobile_component,
            mobile_plate_plane,
            cable["cable_tie_slot_width"],
            cable["cable_tie_slot_length"],
            anchor_x,
            cannon_cable_slot_center_y,
            f"{frame['mobile_plate_thickness']} mm",
            f"Asola_fascetta_ansa_cannone_mobile_{anchor_index:02d}",
        )
    firing_hole_offset_x = (
        firing["pcb_width"] / 2.0 - firing["mounting_hole_edge_inset_x"]
    )
    firing_hole_offset_y = (
        firing["pcb_length"] / 2.0 - firing["mounting_hole_edge_inset_y"]
    )
    firing_hole_centers = (
        (-firing_hole_offset_x, pcb_center_y - firing_hole_offset_y),
        (firing_hole_offset_x, pcb_center_y - firing_hole_offset_y),
        (-firing_hole_offset_x, pcb_center_y + firing_hole_offset_y),
        (firing_hole_offset_x, pcb_center_y + firing_hole_offset_y),
    )
    for index, (center_x, center_y) in enumerate(firing_hole_centers, start=1):
        _cut_round_hole(
            mobile_component,
            mobile_plate_plane,
            firing["mounting_hole_diameter"],
            center_x,
            center_y,
            f"{frame['mobile_plate_thickness']} mm",
            f"Foro_fissaggio_PCB_cannone_{index:02d}",
        )
        _cut_hex_pocket(
            mobile_component,
            mobile_plate_plane,
            rotating["nut_across_flats"],
            center_x,
            center_y,
            f"{rotating['nut_trap_depth']} mm",
            f"Sede_dado_M3_PCB_cannone_{index:02d}",
        )
    # Quattro prefori ciechi M2.2 lasciano 1 mm di pelle superiore sotto il PCB.
    # Le asole sono nelle guance separate: la posizione puo essere registrata
    # senza inventare l'interasse dei piccoli fori del cornetto reale.
    mobile_half_width = mobile_width / 2.0
    adapter_pilot_abs_x = (
        servo["horn_adapter_shelf_inner_x_abs"] + mobile_half_width
    ) / 2.0
    adapter_fastener_y = servo["horn_adapter_fastener_center_y"]
    for side, pilot_x in (
        ("Sinistra", -adapter_pilot_abs_x),
        ("Destra", adapter_pilot_abs_x),
    ):
        for pilot_index, pilot_y in enumerate(
            (-adapter_fastener_y, adapter_fastener_y), start=1
        ):
            _cut_round_hole(
                mobile_component,
                mobile_plate_plane,
                servo["horn_adapter_tray_pilot_diameter"],
                pilot_x,
                pilot_y,
                f"{servo['horn_adapter_tray_pilot_depth']} mm",
                f"Preforo_cieco_guancia_cornetto_{side}_{pilot_index:02d}",
            )

    # 07/08 - Riferimenti hardware mobili: albero di uscita e cornetto a croce
    # originali. I piccoli fori non sono modellati: il pezzo reale fara da dima
    # per viti autofilettanti. L'accesso centrale resta libero per la vite SG90.
    horn_occurrences = []
    horn_reference_specs = (
        (
            7,
            "Sinistro",
            -frame["width"] / 2.0 + frame["wall_thickness"],
            -frame["width"] / 2.0
            + frame["wall_thickness"]
            + servo["shaft_protrusion"],
        ),
        (
            8,
            "Destro",
            frame["width"] / 2.0
            - frame["wall_thickness"]
            - servo["shaft_protrusion"],
            frame["width"] / 2.0
            - frame["wall_thickness"]
            - servo["shaft_protrusion"]
            - servo["horn_reference_thickness"],
        ),
    )
    for number, side, shaft_start_x, horn_start_x in horn_reference_specs:
        horn_occ, horn_component = _new_component_occurrence(
            root,
            f"{number:02d}_Albero_e_cornetto_croce_SG90_{side}_riferimento",
        )
        _cylinder_prism_x(
            horn_component,
            f"Albero_uscita_SG90_{side}",
            f"{shaft_start_x} mm",
            servo["drive_shaft_diameter"],
            0,
            pivot_z,
            f"{servo['shaft_protrusion']} mm",
        )
        _vertical_rectangle_prism_x(
            horn_component,
            f"Cornetto_croce_orizzontale_{side}",
            f"{horn_start_x} mm",
            servo["horn_reference_span"],
            servo["horn_reference_arm_width"],
            0,
            pivot_z,
            f"{servo['horn_reference_thickness']} mm",
        )
        _vertical_rectangle_prism_x(
            horn_component,
            f"Cornetto_croce_verticale_{side}",
            f"{horn_start_x} mm",
            servo["horn_reference_arm_width"],
            servo["horn_reference_span"],
            0,
            pivot_z,
            f"{servo['horn_reference_thickness']} mm",
            adsk.fusion.FeatureOperations.JoinFeatureOperation,
        )
        _cylinder_prism_x(
            horn_component,
            f"Mozzo_cornetto_croce_{side}",
            f"{horn_start_x} mm",
            servo["horn_reference_hub_diameter"],
            0,
            pivot_z,
            f"{servo['horn_reference_thickness']} mm",
            adsk.fusion.FeatureOperations.JoinFeatureOperation,
        )
        horn_occurrences.append(horn_occ)

    # 09A/09B - Guance stampate separatamente. Il disco pieno riceve il
    # cornetto reale mediante viti appuntite; la mensola si avvita sotto la
    # culla tramite due asole da 5 x 2.9 mm. In questo modo non si precaricano
    # assialmente i due servo e si puo centrare la culla prima del serraggio.
    horn_adapter_occurrences = []
    adapter_disc_thickness = servo["horn_adapter_disc_thickness"]
    adapter_outer_abs_x = servo["horn_adapter_outer_face_abs_x"]
    adapter_shelf_inner_abs_x = servo["horn_adapter_shelf_inner_x_abs"]
    adapter_shelf_bottom_z = (
        pivot_z
        - frame["mobile_plate_thickness"] / 2.0
        - servo["horn_adapter_shelf_thickness"]
    )
    adapter_shelf_plane = f"{adapter_shelf_bottom_z} mm"
    adapter_specs = (
        (
            "Sinistra",
            -adapter_outer_abs_x,
            -adapter_outer_abs_x,
            -adapter_shelf_inner_abs_x,
        ),
        (
            "Destra",
            adapter_outer_abs_x - adapter_disc_thickness,
            adapter_shelf_inner_abs_x,
            adapter_outer_abs_x,
        ),
    )
    for side, disc_start_x, shelf_min_x, shelf_max_x in adapter_specs:
        adapter_occ, adapter_component = _new_component_occurrence(
            root, f"09{('A' if side == 'Sinistra' else 'B')}_Guancia_cornetto_{side}_regolabile"
        )
        disc_feature = _cylinder_prism_x(
            adapter_component,
            f"Disco_pieno_cornetto_{side}",
            f"{disc_start_x} mm",
            servo["horn_adapter_disc_diameter"],
            0,
            pivot_z,
            f"{adapter_disc_thickness} mm",
        )
        shelf_width = shelf_max_x - shelf_min_x
        shelf_center_x = (shelf_min_x + shelf_max_x) / 2.0
        shelf_feature = _rectangle_prism_at(
            adapter_component,
            _offset_plane(adapter_component, adapter_shelf_plane),
            f"Mensola_sotto_culla_{side}",
            shelf_width,
            servo["horn_adapter_shelf_length_y"],
            shelf_center_x,
            0,
            f"{servo['horn_adapter_shelf_thickness']} mm",
        )
        _combine_join(
            adapter_component,
            disc_feature.bodies.item(0),
            (shelf_feature,),
            f"Unione_disco_mensola_guancia_{side}",
        )
        _cut_round_hole_x(
            adapter_component,
            f"{disc_start_x} mm",
            servo["horn_adapter_center_access_diameter"],
            0,
            pivot_z,
            f"{adapter_disc_thickness} mm",
            f"Accesso_vite_centrale_cornetto_{side}",
        )
        for slot_index, slot_y in enumerate(
            (-adapter_fastener_y, adapter_fastener_y), start=1
        ):
            _cut_rectangle(
                adapter_component,
                _offset_plane(adapter_component, adapter_shelf_plane),
                servo["horn_adapter_adjustment_slot_length"],
                servo["horn_adapter_adjustment_slot_width"],
                -adapter_pilot_abs_x if side == "Sinistra" else adapter_pilot_abs_x,
                slot_y,
                f"{servo['horn_adapter_shelf_thickness']} mm",
                f"Asola_regolazione_guancia_{side}_{slot_index:02d}",
            )
        if adapter_component.bRepBodies.count != 1:
            raise RuntimeError(f"La guancia cornetto {side} deve essere un unico corpo stampabile.")
        horn_adapter_occurrences.append(adapter_occ)

    # 10 - Gruppo reale del cannone: PCB, solenoide e canna tubolare sono
    # componenti rigidi fra loro e inclinano tutti insieme con la culla.
    cannon_occ, cannon_component = _new_component_occurrence(
        root, "10_Modulo_cannone_reale_PCB_solenoide_canna"
    )
    pcb_bottom_z = pivot_z + frame["mobile_plate_thickness"] / 2.0
    pcb_plane = _offset_plane(cannon_component, f"{pcb_bottom_z} mm")
    _rectangle_prism_at(
        cannon_component,
        pcb_plane,
        "PCB_modulo_cannone_50x50",
        firing["pcb_width"],
        firing["pcb_length"],
        0,
        pcb_center_y,
        "pcb_cannone_spessore",
    )
    for index, (center_x, center_y) in enumerate(firing_hole_centers, start=1):
        _cut_round_hole(
            cannon_component,
            pcb_plane,
            firing["mounting_hole_diameter"],
            center_x,
            center_y,
            "pcb_cannone_spessore",
            f"Foro_PCB_reale_{index:02d}",
        )

    support_height = (
        firing["overall_height_from_pcb_bottom"]
        - firing["pcb_thickness"]
        - firing["cannon_outer_diameter_at_solenoid"]
    )
    if support_height < 0:
        raise RuntimeError(
            "Altezza modulo cannone insufficiente per PCB e diametro solenoide"
        )
    if support_height > 0:
        support_plane = _offset_plane(
            cannon_component, f"{pcb_bottom_z + firing['pcb_thickness']} mm"
        )
        _rectangle_prism_at(
            cannon_component,
            support_plane,
            "Appoggio_solenoide_su_PCB",
            firing["cannon_outer_diameter_at_solenoid"],
            firing["solenoid_length"],
            0,
            pcb_center_y,
            f"{support_height} mm",
        )

    solenoid_center_z = (
        pcb_bottom_z
        + firing["overall_height_from_pcb_bottom"]
        - firing["cannon_outer_diameter_at_solenoid"] / 2.0
    )
    solenoid_start_y = pcb_center_y - firing["solenoid_length"] / 2.0
    solenoid_start_expression = f"{solenoid_start_y} mm"
    _cylinder_prism_y(
        cannon_component,
        "Corpo_solenoide_riferimento",
        solenoid_start_expression,
        firing["cannon_outer_diameter_at_solenoid"],
        0,
        solenoid_center_z,
        "solenoide_lunghezza",
    )
    _cut_round_hole_y(
        cannon_component,
        solenoid_start_expression,
        firing["barrel_outer_diameter"],
        0,
        solenoid_center_z,
        "solenoide_lunghezza",
        "Passaggio_canna_nel_solenoide",
    )

    barrel_start_y = pcb_center_y + firing["solenoid_length"] / 2.0
    barrel_start_expression = f"{barrel_start_y} mm"
    _cylinder_prism_y(
        cannon_component,
        "Canna_tubolare_esterna",
        barrel_start_expression,
        firing["barrel_outer_diameter"],
        0,
        solenoid_center_z,
        "canna_sporgenza",
    )
    _cut_round_hole_y(
        cannon_component,
        barrel_start_expression,
        firing["barrel_inner_diameter"],
        0,
        solenoid_center_z,
        "canna_sporgenza",
        "Foro_interno_canna_tubolare",
    )

    # 11/12/13 - Guscio fisso removibile della torretta. Il cofano posteriore
    # protegge il telaio; i due carter laterali usano viti M2.5 dedicate sulle
    # guide fisse SG90 e restano aperti inferiormente per i cavi.
    turret_shell_wall = holder_wall
    turret_shell_clearance = servo_clearance
    barrel_shell_hole_diameter = (
        firing["barrel_outer_diameter"] + 2.0 * turret_shell_clearance
    )
    _add_user_parameter(
        design,
        "guscio_torretta_parete",
        turret_shell_wall,
        "mm",
        "Gusci removibili torretta",
    )
    _add_user_parameter(
        design,
        "guscio_torretta_gioco",
        turret_shell_clearance,
        "mm",
        "Gioco attorno a telaio, servo e modulo mobile",
    )
    _add_user_parameter(
        design,
        "guscio_cannone_foro_canna",
        barrel_shell_hole_diameter,
        "mm",
        "Passaggio canna nel guscio mobile",
    )

    cage_min_y = servo_center_y - cage_overall_length / 2.0
    cage_max_y = servo_center_y + cage_overall_length / 2.0
    carter_min_y = cage_min_y - turret_shell_clearance - turret_shell_wall
    carter_max_y = cage_max_y + turret_shell_clearance + turret_shell_wall
    carter_length = carter_max_y - carter_min_y
    carter_center_y = (carter_min_y + carter_max_y) / 2.0
    cage_bottom_z = bottom_shelf_z
    cage_top_z = top_shelf_z + holder_shelf
    carter_bottom_z = cage_bottom_z - turret_shell_clearance
    carter_roof_bottom_z = cage_top_z + turret_shell_clearance
    carter_top_z = carter_roof_bottom_z + turret_shell_wall
    carter_height = carter_top_z - carter_bottom_z
    carter_center_z = (carter_bottom_z + carter_top_z) / 2.0

    hood_inner_width = frame["width"] + 2.0 * turret_shell_clearance
    hood_outer_width = hood_inner_width + 2.0 * turret_shell_wall
    hood_back_inner_y = -frame["length"] / 2.0 - turret_shell_clearance
    hood_back_outer_y = hood_back_inner_y - turret_shell_wall
    hood_front_y = carter_min_y
    hood_depth = hood_front_y - hood_back_outer_y
    if hood_depth <= turret_shell_wall:
        raise RuntimeError("Profondita del cofano posteriore torretta insufficiente")
    hood_center_y = (hood_back_outer_y + hood_front_y) / 2.0
    hood_bottom_z = fixed_base_top
    hood_roof_bottom_z = (
        fixed_base_top + frame["height"] + turret_shell_clearance
    )
    hood_top_z = hood_roof_bottom_z + turret_shell_wall
    hood_height = hood_top_z - hood_bottom_z
    hood_center_z = (hood_bottom_z + hood_top_z) / 2.0

    hood_occ, hood_component = _new_component_occurrence(
        root, "11_Guscio_fisso_posteriore_torretta_removibile"
    )
    _vertical_rectangle_prism_y(
        hood_component,
        "Parete_posteriore_guscio_torretta",
        f"{hood_back_outer_y} mm",
        hood_outer_width,
        hood_height,
        0,
        hood_center_z,
        f"{turret_shell_wall} mm",
    )
    hood_left_x = -hood_outer_width / 2.0
    hood_right_x = hood_inner_width / 2.0
    for side, plane_x in (("Sinistra", hood_left_x), ("Destra", hood_right_x)):
        _vertical_rectangle_prism_x(
            hood_component,
            f"Fianco_cofano_{side}",
            f"{plane_x} mm",
            hood_depth,
            hood_height,
            hood_center_y,
            hood_center_z,
            f"{turret_shell_wall} mm",
            adsk.fusion.FeatureOperations.JoinFeatureOperation,
        )
    hood_roof_plane = _offset_plane(hood_component, f"{hood_roof_bottom_z} mm")
    _rectangle_prism_at(
        hood_component,
        hood_roof_plane,
        "Tetto_cofano_posteriore",
        hood_outer_width,
        hood_depth,
        0,
        hood_center_y,
        f"{turret_shell_wall} mm",
        adsk.fusion.FeatureOperations.JoinFeatureOperation,
    )
    hood_screw_z_values = (
        fixed_base_top + 5.0,
        fixed_base_top + frame["height"] - 5.0,
    )
    hood_screw_y = hood_front_y - turret_shell_wall
    for side, shell_plane_x, fixed_plane_x in (
        ("Sinistra", hood_left_x, left_wall_x),
        ("Destra", hood_right_x, right_wall_x),
    ):
        for index, screw_z in enumerate(hood_screw_z_values, start=1):
            _cut_round_hole_x(
                hood_component,
                f"{shell_plane_x} mm",
                servo["carter_screw_clearance_hole_diameter"],
                hood_screw_y,
                screw_z,
                f"{turret_shell_wall} mm",
                f"Foro_M2_5_cofano_{side}_{index:02d}",
            )
            _cut_round_hole_x(
                fixed_component,
                f"{fixed_plane_x} mm",
                servo["carter_screw_pilot_hole_diameter"],
                hood_screw_y,
                screw_z,
                f"{frame['wall_thickness']} mm",
                f"Preforo_M2_5_cofano_telaio_{side}_{index:02d}",
            )

    fixed_shell_occurrences = [hood_occ]
    left_carter_outer_x = (
        left_cage_outer_x - turret_shell_clearance - turret_shell_wall
    )
    left_carter_inner_x = -frame_outer_x - turret_shell_clearance
    right_carter_inner_x = frame_outer_x + turret_shell_clearance
    right_carter_outer_x = (
        right_cage_outer_x + turret_shell_clearance + turret_shell_wall
    )
    carter_specs = (
        (
            "Sinistro",
            left_carter_outer_x,
            left_carter_inner_x,
            left_carter_outer_x,
        ),
        (
            "Destro",
            right_carter_inner_x,
            right_carter_outer_x,
            right_carter_outer_x - turret_shell_wall,
        ),
    )
    for number, (side, minimum_x, maximum_x, outer_wall_x) in enumerate(
        carter_specs,
        start=12,
    ):
        carter_occ, carter_component = _new_component_occurrence(
            root, f"{number:02d}_Carter_SG90_{side}_removibile"
        )
        carter_width = maximum_x - minimum_x
        carter_center_x = (minimum_x + maximum_x) / 2.0
        _vertical_rectangle_prism_x(
            carter_component,
            f"Parete_esterna_carter_{side}",
            f"{outer_wall_x} mm",
            carter_length,
            carter_height,
            carter_center_y,
            carter_center_z,
            f"{turret_shell_wall} mm",
        )
        for end_name, plane_y in (
            ("Posteriore", carter_min_y),
            ("Anteriore", carter_max_y - turret_shell_wall),
        ):
            _vertical_rectangle_prism_y(
                carter_component,
                f"Parete_{end_name}_carter_{side}",
                f"{plane_y} mm",
                carter_width,
                carter_height,
                carter_center_x,
                carter_center_z,
                f"{turret_shell_wall} mm",
                adsk.fusion.FeatureOperations.JoinFeatureOperation,
            )
        carter_roof_plane = _offset_plane(
            carter_component, f"{carter_roof_bottom_z} mm"
        )
        _rectangle_prism_at(
            carter_component,
            carter_roof_plane,
            f"Tetto_carter_{side}",
            carter_width,
            carter_length,
            carter_center_x,
            carter_center_y,
            f"{turret_shell_wall} mm",
            adsk.fusion.FeatureOperations.JoinFeatureOperation,
        )
        for index, screw_center_y in enumerate(rail_centers_y, start=1):
            _cut_round_hole_x(
                carter_component,
                f"{outer_wall_x} mm",
                servo["carter_screw_clearance_hole_diameter"],
                screw_center_y,
                pivot_z,
                f"{turret_shell_wall} mm",
                f"Foro_M2_5_carter_{side}_{index:02d}",
            )
        fixed_shell_occurrences.append(carter_occ)

    # 14 - Guscio mobile aperto inferiormente. Protegge PCB e solenoide,
    # ruota rigidamente con la culla e lascia libera l'ansa dei cavi.
    moving_outer_width = (
        firing["pcb_width"]
        + 2.0 * turret_shell_clearance
        + 2.0 * turret_shell_wall
    )
    moving_outer_length = (
        firing["pcb_length"]
        + 2.0 * turret_shell_clearance
        + 2.0 * turret_shell_wall
    )
    moving_bottom_z = pcb_bottom_z
    moving_roof_bottom_z = (
        pcb_bottom_z
        + firing["overall_height_from_pcb_bottom"]
        + turret_shell_clearance
    )
    moving_top_z = moving_roof_bottom_z + turret_shell_wall
    moving_height = moving_top_z - moving_bottom_z
    moving_center_z = (moving_bottom_z + moving_top_z) / 2.0
    moving_min_y = pcb_center_y - moving_outer_length / 2.0
    moving_max_y = pcb_center_y + moving_outer_length / 2.0

    # Culatta di servizio: l'accesso è ricavato nella zona posteriore-alta del
    # guscio mobile, mentre una guida corta rimane interamente all'interno. Il
    # coperchio a L torna a filo con l'inviluppo originale, quindi non riduce il
    # margine dinamico già piccolo verso il cofano fisso a elevazione massima.
    loader_guide_end_y = solenoid_start_y - loader["guide_to_solenoid_clearance"]
    loader_guide_start_y = loader_guide_end_y - loader["guide_length"]
    moving_rear_inner_y = moving_min_y + turret_shell_wall
    if loader_guide_start_y < moving_rear_inner_y + 2.0:
        raise RuntimeError("La guida culatta non lascia spazio di accesso dietro al guscio.")
    service_access_gap = moving_min_y - hood_front_y
    if loader["provisional_max_projectile_length"] > service_access_gap - 2.0:
        raise RuntimeError("Il proiettile provvisorio non entra nel varco di servizio superiore.")

    loader_window_bottom_z = (
        moving_bottom_z + loader["rear_window_bottom_above_shroud_bottom"]
    )
    loader_window_top_z = moving_top_z
    loader_window_height = loader_window_top_z - loader_window_bottom_z
    loader_window_center_z = (loader_window_bottom_z + loader_window_top_z) / 2.0
    cable_notch_top_z = moving_bottom_z + cable["cannon_mobile_passage_length"]
    if loader_window_bottom_z - cable_notch_top_z < 2.0:
        raise RuntimeError("Culatta e tacca cavo lasciano un legamento posteriore insufficiente.")
    loader_roof_slot_center_y = moving_min_y + loader["roof_slot_length"] / 2.0
    loader_pocket_center_y = (
        moving_min_y + loader["hatch_top_pocket_length"] / 2.0
    )
    loader_screw_center_y = (
        moving_min_y + loader["mounting_hole_center_from_rear_edge"]
    )
    loader_screw_centers = (
        (-loader["mounting_hole_spacing"] / 2.0, loader_screw_center_y),
        (loader["mounting_hole_spacing"] / 2.0, loader_screw_center_y),
    )
    reinforcement_end_y = (
        moving_min_y + loader["hatch_local_reinforcement_length"]
    )
    if reinforcement_end_y > solenoid_start_y - 0.2:
        raise RuntimeError("Il rinforzo della tasca culatta invade il solenoide.")
    pcb_boss_radius = data["base_standoffs"]["outer_diameter"] / 2.0
    loader_boss_radius = loader["screw_boss_diameter"] / 2.0
    for loader_x, loader_y in loader_screw_centers:
        for pcb_x, pcb_y in firing_hole_centers:
            boss_clearance = math.hypot(loader_x - pcb_x, loader_y - pcb_y) - (
                loader_boss_radius + pcb_boss_radius
            )
            if boss_clearance < loader["minimum_printed_wall"]:
                raise RuntimeError("Un boss M2.5 della culatta è troppo vicino a un boss M3.")
    if loader["hatch_vertical_plate_thickness"] > turret_shell_wall - 0.3:
        raise RuntimeError("Il coperchio culatta non conserva gioco nella parete posteriore.")

    moving_shroud_occ, moving_shroud_component = _new_component_occurrence(
        root, "14_Guscio_mobile_cannone_removibile"
    )
    moving_zero_plane = _offset_plane(
        moving_shroud_component, f"{moving_bottom_z} mm"
    )
    moving_side_x = (moving_outer_width - turret_shell_wall) / 2.0
    moving_end_y = (moving_outer_length - turret_shell_wall) / 2.0
    _rectangle_prism_at(
        moving_shroud_component,
        moving_zero_plane,
        "Parete_mobile_Ovest",
        turret_shell_wall,
        moving_outer_length,
        -moving_side_x,
        pcb_center_y,
        f"{moving_height} mm",
    )
    _rectangle_prism_at(
        moving_shroud_component,
        moving_zero_plane,
        "Parete_mobile_Posteriore",
        moving_outer_width,
        turret_shell_wall,
        0,
        pcb_center_y - moving_end_y,
        f"{moving_height} mm",
        adsk.fusion.FeatureOperations.JoinFeatureOperation,
    )
    _rectangle_prism_at(
        moving_shroud_component,
        moving_zero_plane,
        "Parete_mobile_Est",
        turret_shell_wall,
        moving_outer_length,
        moving_side_x,
        pcb_center_y,
        f"{moving_height} mm",
        adsk.fusion.FeatureOperations.JoinFeatureOperation,
    )
    # Le due guance/dischi di elevazione attraversano localmente le pareti del
    # guscio mobile. Due scassi circolari con 0.5 mm di gioco evitano qualsiasi
    # compenetrazione e permettono di montare il guscio dopo aver centrato i
    # cornetti reali dei servo.
    horn_adapter_shroud_clearance_diameter = (
        servo["horn_adapter_disc_diameter"] + 2.0 * turret_shell_clearance
    )
    for side, shroud_wall_start_x in (
        ("Ovest", -moving_outer_width / 2.0),
        ("Est", moving_outer_width / 2.0 - turret_shell_wall),
    ):
        _cut_round_hole_x(
            moving_shroud_component,
            f"{shroud_wall_start_x} mm",
            horn_adapter_shroud_clearance_diameter,
            0,
            pivot_z,
            f"{turret_shell_wall} mm",
            f"Scasso_guancia_elevazione_{side}",
        )
    moving_roof_plane = _offset_plane(
        moving_shroud_component, f"{moving_roof_bottom_z} mm"
    )
    _rectangle_prism_at(
        moving_shroud_component,
        moving_roof_plane,
        "Tetto_guscio_mobile_cannone",
        moving_outer_width,
        moving_outer_length,
        0,
        pcb_center_y,
        f"{turret_shell_wall} mm",
        adsk.fusion.FeatureOperations.JoinFeatureOperation,
    )

    # Rinforzo a U sotto la tasca: due longheroni laterali e una traversa
    # anteriore portano boss e nervatura senza richiudere l'asola centrale.
    reinforcement_bottom_z = (
        moving_roof_bottom_z - loader["hatch_local_reinforcement_thickness"]
    )
    reinforcement_plane = _offset_plane(
        moving_shroud_component, f"{reinforcement_bottom_z} mm"
    )
    reinforcement_side_width = (
        loader["hatch_top_pocket_width"] - loader["rear_window_width"]
    ) / 2.0
    if reinforcement_side_width < loader["minimum_printed_wall"]:
        raise RuntimeError("I longheroni sotto la tasca culatta sono troppo stretti.")
    reinforcement_side_center_x = (
        loader["rear_window_width"] / 2.0 + reinforcement_side_width / 2.0
    )
    reinforcement_center_y = (
        moving_min_y + loader["hatch_local_reinforcement_length"] / 2.0
    )
    for side, center_x in (
        ("Ovest", -reinforcement_side_center_x),
        ("Est", reinforcement_side_center_x),
    ):
        _rectangle_prism_at(
            moving_shroud_component,
            reinforcement_plane,
            f"Longherone_rinforzo_tasca_culatta_{side}",
            reinforcement_side_width,
            loader["hatch_local_reinforcement_length"],
            center_x,
            reinforcement_center_y,
            f"{loader['hatch_local_reinforcement_thickness'] + 0.2} mm",
            adsk.fusion.FeatureOperations.JoinFeatureOperation,
        )
    reinforcement_front_length = (
        loader["hatch_local_reinforcement_length"] - loader["roof_slot_length"]
    )
    reinforcement_front_center_y = (
        moving_min_y
        + loader["roof_slot_length"]
        + reinforcement_front_length / 2.0
    )
    _rectangle_prism_at(
        moving_shroud_component,
        reinforcement_plane,
        "Traversa_anteriore_rinforzo_tasca_culatta",
        loader["hatch_top_pocket_width"],
        reinforcement_front_length,
        0,
        reinforcement_front_center_y,
        f"{loader['hatch_local_reinforcement_thickness'] + 0.2} mm",
        adsk.fusion.FeatureOperations.JoinFeatureOperation,
    )

    # Apertura di servizio a L: finestra posteriore fino al tetto, asola
    # superiore contigua e tasca poco profonda per un coperchio completamente
    # a filo. La tacca 6x4 dei cavi rimane separata più in basso.
    _cut_vertical_rectangle_y(
        moving_shroud_component,
        f"{moving_min_y} mm",
        loader["rear_window_width"],
        loader_window_height,
        0,
        loader_window_center_z,
        f"{turret_shell_wall} mm",
        "Finestra_posteriore_culatta_manuale",
    )
    _cut_rectangle(
        moving_shroud_component,
        moving_roof_plane,
        loader["rear_window_width"],
        loader["roof_slot_length"],
        0,
        loader_roof_slot_center_y,
        f"{turret_shell_wall} mm",
        "Asola_tetto_accesso_culatta_manuale",
    )
    hatch_pocket_bottom_z = moving_top_z - loader["hatch_top_pocket_depth"]
    hatch_pocket_plane = _offset_plane(
        moving_shroud_component, f"{hatch_pocket_bottom_z} mm"
    )
    _cut_rectangle(
        moving_shroud_component,
        hatch_pocket_plane,
        loader["hatch_top_pocket_width"],
        loader["hatch_top_pocket_length"],
        0,
        loader_pocket_center_y,
        f"{loader['hatch_top_pocket_depth']} mm",
        "Tasca_coperchio_culatta_a_filo",
    )

    # Guida corta coassiale, sostenuta dal tetto del guscio mobile. Non sporge
    # posteriormente e termina con gioco prima del solenoide reale.
    _cylinder_prism_y(
        moving_shroud_component,
        "Guida_interna_culatta_manuale",
        f"{loader_guide_start_y} mm",
        loader["guide_outer_diameter"],
        0,
        solenoid_center_z,
        f"{loader['guide_length']} mm",
    )
    _cut_round_hole_y(
        moving_shroud_component,
        f"{loader_guide_start_y} mm",
        loader["guide_inner_diameter"],
        0,
        solenoid_center_z,
        f"{loader['guide_length']} mm",
        "Foro_coassiale_guida_culatta_manuale",
    )
    guide_rib_bottom_z = (
        solenoid_center_z
        + loader["guide_outer_diameter"] / 2.0
        - loader["guide_roof_rib_overlap"]
    )
    guide_rib_height = moving_roof_bottom_z - guide_rib_bottom_z + 0.2
    guide_rib_plane = _offset_plane(
        moving_shroud_component, f"{guide_rib_bottom_z} mm"
    )
    _rectangle_prism_at(
        moving_shroud_component,
        guide_rib_plane,
        "Nervatura_tetto_guida_culatta",
        loader["guide_roof_rib_width"],
        loader["guide_length"],
        0,
        (loader_guide_start_y + loader_guide_end_y) / 2.0,
        f"{guide_rib_height} mm",
        adsk.fusion.FeatureOperations.JoinFeatureOperation,
    )

    # Due boss interni ricevono le M2.5 del coperchio dall'alto. Rimangono ai
    # lati dell'asola e lontani dal solenoide e dai boss M3 del PCB.
    hatch_boss_bottom_z = moving_roof_bottom_z - loader["screw_boss_height"]
    hatch_boss_plane = _offset_plane(
        moving_shroud_component, f"{hatch_boss_bottom_z} mm"
    )
    for index, (screw_x, screw_y) in enumerate(loader_screw_centers, start=1):
        _cylinder_prism(
            moving_shroud_component,
            hatch_boss_plane,
            f"Boss_M2_5_coperchio_culatta_{index:02d}",
            loader["screw_boss_diameter"],
            screw_x,
            screw_y,
            f"{loader['screw_boss_height'] + 0.2} mm",
            adsk.fusion.FeatureOperations.JoinFeatureOperation,
        )
        _cut_round_hole(
            moving_shroud_component,
            hatch_boss_plane,
            loader["pilot_hole_diameter"],
            screw_x,
            screw_y,
            f"{loader['screw_boss_height'] + 0.6} mm",
            f"Preforo_M2_5_coperchio_culatta_{index:02d}",
        )
    moving_front_wall_start_y = moving_max_y - turret_shell_wall
    # La parete anteriore nasce già come tre solidi uniti attorno a una cava U
    # quadrata. Evitiamo così un taglio coincidente con la canna reale, che in
    # STEP poteva spezzare il tubo nel tratto spesso quanto la parete.
    front_side_width = (
        moving_outer_width - barrel_shell_hole_diameter
    ) / 2.0
    front_side_center_x = (
        barrel_shell_hole_diameter / 2.0 + front_side_width / 2.0
    )
    front_wall_center_y = pcb_center_y + moving_end_y
    for side, center_x in (
        ("Ovest", -front_side_center_x),
        ("Est", front_side_center_x),
    ):
        _rectangle_prism_at(
            moving_shroud_component,
            moving_zero_plane,
            f"Parete_mobile_Anteriore_{side}",
            front_side_width,
            turret_shell_wall,
            center_x,
            front_wall_center_y,
            f"{moving_height} mm",
            adsk.fusion.FeatureOperations.JoinFeatureOperation,
        )
    front_bridge_bottom_z = (
        solenoid_center_z + barrel_shell_hole_diameter / 2.0
    )
    front_bridge_height = moving_top_z - front_bridge_bottom_z
    if front_bridge_height <= turret_shell_wall:
        raise RuntimeError("Il ponte sopra la cava canna non è stampabile.")
    front_bridge_plane = _offset_plane(
        moving_shroud_component, f"{front_bridge_bottom_z} mm"
    )
    _rectangle_prism_at(
        moving_shroud_component,
        front_bridge_plane,
        "Ponte_superiore_cava_U_canna",
        barrel_shell_hole_diameter,
        turret_shell_wall,
        0,
        front_wall_center_y,
        f"{front_bridge_height} mm",
        adsk.fusion.FeatureOperations.JoinFeatureOperation,
    )
    _cut_vertical_rectangle_y(
        moving_shroud_component,
        f"{moving_min_y} mm",
        cable["cannon_mobile_passage_width"],
        cable["cannon_mobile_passage_length"],
        0,
        moving_bottom_z + cable["cannon_mobile_passage_length"] / 2.0,
        f"{turret_shell_wall} mm",
        "Tacca_posteriore_cavo_cannone_aperta_inferiormente",
    )

    boss_plane_z = pcb_bottom_z + firing["pcb_thickness"]
    boss_plane = _offset_plane(moving_shroud_component, f"{boss_plane_z} mm")
    boss_height = moving_roof_bottom_z - boss_plane_z + 0.2
    boss_hole_depth = moving_top_z - boss_plane_z
    boss_diameter = data["base_standoffs"]["outer_diameter"]
    for index, (center_x, center_y) in enumerate(firing_hole_centers, start=1):
        _cylinder_prism(
            moving_shroud_component,
            boss_plane,
            f"Colonna_M3_guscio_mobile_{index:02d}",
            boss_diameter,
            center_x,
            center_y,
            f"{boss_height} mm",
            adsk.fusion.FeatureOperations.JoinFeatureOperation,
        )
        _cut_round_hole(
            moving_shroud_component,
            boss_plane,
            firing["mounting_hole_diameter"],
            center_x,
            center_y,
            f"{boss_hole_depth} mm",
            f"Foro_M3_guscio_mobile_{index:02d}",
        )

    # 15 - Coperchio a L removibile della culatta. Riempie la tasca superiore
    # e la finestra posteriore senza oltrepassare l'inviluppo del guscio.
    hatch_occ, hatch_component = _new_component_occurrence(
        root, "15_Coperchio_culatta_L_removibile_M2_5"
    )
    hatch_clearance = loader["hatch_clearance_per_side"]
    hatch_top_width = loader["hatch_top_pocket_width"] - 2.0 * hatch_clearance
    hatch_top_length = loader["hatch_top_pocket_length"] - 2.0 * hatch_clearance
    hatch_top_plane = _offset_plane(hatch_component, f"{hatch_pocket_bottom_z} mm")
    _rectangle_prism_at(
        hatch_component,
        hatch_top_plane,
        "Piastra_superiore_coperchio_culatta_a_filo",
        hatch_top_width,
        hatch_top_length,
        0,
        loader_pocket_center_y,
        f"{loader['hatch_top_plate_thickness']} mm",
    )
    hatch_vertical_width = loader["rear_window_width"] - 2.0 * hatch_clearance
    hatch_vertical_height = loader_window_height - 2.0 * hatch_clearance
    _vertical_rectangle_prism_y(
        hatch_component,
        "Piastra_posteriore_coperchio_culatta",
        f"{moving_min_y + hatch_clearance} mm",
        hatch_vertical_width,
        hatch_vertical_height,
        0,
        loader_window_center_z,
        f"{loader['hatch_vertical_plate_thickness']} mm",
        adsk.fusion.FeatureOperations.JoinFeatureOperation,
    )
    hatch_cap_top_z = hatch_pocket_bottom_z + loader["hatch_top_plate_thickness"]
    hatch_countersink_bottom_plane = _offset_plane(
        hatch_component, f"{hatch_cap_top_z - loader['countersink_depth']} mm"
    )
    hatch_top_surface_plane = _offset_plane(hatch_component, f"{hatch_cap_top_z} mm")
    for index, (screw_x, screw_y) in enumerate(loader_screw_centers, start=1):
        _cut_round_hole(
            hatch_component,
            hatch_top_plane,
            loader["clearance_hole_diameter"],
            screw_x,
            screw_y,
            f"{loader['hatch_top_plate_thickness']} mm",
            f"Foro_M2_5_coperchio_culatta_{index:02d}",
        )
        _cut_countersink_frustum(
            hatch_component,
            hatch_countersink_bottom_plane,
            hatch_top_surface_plane,
            loader["clearance_hole_diameter"],
            loader["countersink_diameter"],
            screw_x,
            screw_y,
            f"Svasatura_M2_5_coperchio_culatta_{index:02d}",
        )
    if moving_shroud_component.bRepBodies.count != 1:
        raise RuntimeError("Guscio mobile, guida culatta e relativi boss devono essere un corpo.")
    if hatch_component.bRepBodies.count != 1:
        raise RuntimeError("Il coperchio a L della culatta deve essere un unico corpo stampabile.")

    # Giunti reali dell'assieme: azimut Z e elevazione X. Gli altri componenti
    # sono resi rigidi rispetto al gruppo corretto.
    _add_as_built_rigid_joint(
        root, cover_occ, stepper_occ, "Rigido_coperchio_stepper"
    )
    _add_as_built_rigid_joint(
        root, cover_occ, thrust_occ, "Rigido_tetto_rondella_assiale"
    )
    for index, clip_occ in enumerate(anti_lift_clip_occurrences, start=1):
        _add_as_built_rigid_joint(
            root,
            cover_occ,
            clip_occ,
            f"Rigido_tetto_fermaglio_anti_sollevamento_{index:02d}",
        )
    azimuth_axis_sketch = root.sketches.add(root.xZConstructionPlane)
    azimuth_axis_sketch.name = "Asse_azimut_Z"
    azimuth_axis_line = azimuth_axis_sketch.sketchCurves.sketchLines.addByTwoPoints(
        adsk.core.Point3D.create(0, _mm_to_cm(-20), 0),
        adsk.core.Point3D.create(0, _mm_to_cm(20), 0),
    )
    azimuth_axis_sketch.isVisible = False
    azimuth_geometry = adsk.fusion.JointGeometry.createByCurve(
        azimuth_axis_line,
        adsk.fusion.JointKeyPointTypes.MiddleKeyPoint,
    )
    _validate_sketch_line_world_axis(
        azimuth_axis_line,
        (0.0, 0.0, 1.0),
        "Rotazione_orizzontale_albero_stepper_Z",
    )
    azimuth_joint = _add_as_built_revolute_joint(
        root,
        stepper_occ,
        rotor_occ,
        "Rotazione_orizzontale_albero_stepper_Z",
        adsk.fusion.JointDirections.CustomJointDirection,
        azimuth_geometry,
        custom_axis=azimuth_axis_line,
        minimum_deg=-cable["azimuth_rotation_range_deg"] / 2.0,
        maximum_deg=cable["azimuth_rotation_range_deg"] / 2.0,
    )
    _add_as_built_rigid_joint(
        root, rotor_occ, adapter_occ, "Rigido_albero_stepper_base_D100"
    )
    _add_as_built_rigid_joint(
        root, adapter_occ, fixed_occ, "Rigido_adattatore_torretta_fissa"
    )
    for index, servo_occ in enumerate(servo_occurrences, start=1):
        _add_as_built_rigid_joint(
            root, fixed_occ, servo_occ, f"Rigido_servo_esterno_{index:02d}"
        )
    for index, (adapter_horn_occ, horn_occ) in enumerate(
        zip(horn_adapter_occurrences, horn_occurrences), start=1
    ):
        _add_as_built_rigid_joint(
            root,
            mobile_occ,
            adapter_horn_occ,
            f"Rigido_culla_guancia_cornetto_{index:02d}",
        )
        _add_as_built_rigid_joint(
            root,
            adapter_horn_occ,
            horn_occ,
            f"Rigido_guancia_cornetto_reale_{index:02d}",
        )
    for index, shell_occ in enumerate(fixed_shell_occurrences, start=1):
        _add_as_built_rigid_joint(
            root,
            fixed_occ,
            shell_occ,
            f"Rigido_guscio_torretta_fisso_{index:02d}",
        )

    elevation_axis_plane = _offset_plane(root, f"{pivot_z} mm")
    elevation_axis_sketch = root.sketches.add(elevation_axis_plane)
    elevation_axis_sketch.name = "Asse_elevazione_X"
    elevation_axis_line = elevation_axis_sketch.sketchCurves.sketchLines.addByTwoPoints(
        adsk.core.Point3D.create(_mm_to_cm(-20), 0, 0),
        adsk.core.Point3D.create(_mm_to_cm(20), 0, 0),
    )
    elevation_axis_sketch.isVisible = False
    elevation_geometry = adsk.fusion.JointGeometry.createByCurve(
        elevation_axis_line,
        adsk.fusion.JointKeyPointTypes.MiddleKeyPoint,
    )
    _validate_sketch_line_world_axis(
        elevation_axis_line,
        (1.0, 0.0, 0.0),
        "Elevazione_cannone_asse_X_con_due_servo",
    )
    elevation_joint = _add_as_built_revolute_joint(
        root,
        fixed_occ,
        mobile_occ,
        "Elevazione_cannone_asse_X_con_due_servo",
        adsk.fusion.JointDirections.CustomJointDirection,
        elevation_geometry,
        custom_axis=elevation_axis_line,
        minimum_deg=cannon["elevation_min_deg"],
        maximum_deg=cannon["elevation_max_deg"],
    )
    _add_as_built_rigid_joint(
        root, mobile_occ, cannon_occ, "Rigido_culla_PCB_solenoide_canna"
    )
    _add_as_built_rigid_joint(
        root,
        mobile_occ,
        moving_shroud_occ,
        "Rigido_culla_guscio_mobile_cannone",
    )
    _add_as_built_rigid_joint(
        root,
        mobile_occ,
        hatch_occ,
        "Rigido_culla_coperchio_culatta_chiuso",
    )

    # Durante il funzionamento il tetto e lo statore sono fissi. Il tetto resta
    # comunque un componente removibile fisicamente: Ground To Parent serve
    # soltanto a rendere non ambigua la simulazione cinematica di Fusion.
    if not cover_occ.isGroundToParent:
        raise RuntimeError("Fusion non ha fissato il tetto al sottoassieme padre.")

    return document, design


def _create_full_reference_subassemblies(document, design, root, data):
    """Aggiunge guscio, riferimenti e torretta; la batteria è già integrata."""
    _validate_lower_deck_layout(data)
    _validate_hull_shell(data)
    lower = data["chassis"]["lower_deck"]
    upper = data["chassis"]["upper_deck"]

    _create_continuous_hull_shell(design, root, data)

    # Il profilo Arduino è posizionato in XY sul piano inferiore, ma resta uno
    # schizzo: non viene inventata la quota Z fisica prima di conoscere le
    # colonnine e l'altezza complessiva Arduino + shield.
    _create_arduino_plan_reference(design, root, data, lower["thickness"])

    upper_top_z = (
        lower["thickness"]
        + upper["clearance_above_lower"]
        + upper["thickness"]
    )
    turret_transform = _translation_matrix(0, 0, upper_top_z)
    turret_parent_occ, turret_parent = _new_component_occurrence(
        root,
        "06_Sottoassieme_coperchio_stepper_torretta",
        turret_transform,
    )
    # Ancora l'intero sottoassieme al carro prima della costruzione interna.
    # I gradi di liberta restano soltanto nei due giunti rotore e culla.
    turret_parent_occ.isGroundToParent = True
    if not turret_parent_occ.isGroundToParent:
        raise RuntimeError(
            "Fusion non ha fissato subito il sottoassieme tetto-torretta al carro."
        )
    _create_cover_and_modular_turret(
        document,
        design,
        turret_parent,
        data,
    )
    if not turret_parent_occ.isGroundToParent:
        raise RuntimeError(
            "Fusion non ha fissato il sottoassieme tetto-torretta al carro."
        )


def _create_design(data):
    app = adsk.core.Application.get()
    document = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
    design = adsk.fusion.Design.cast(app.activeProduct)
    if not design:
        raise RuntimeError("Impossibile creare un documento Fusion Design")

    design.designType = adsk.fusion.DesignTypes.ParametricDesignType
    root = design.rootComponent

    build_stage = data["meta"]["build_stage"]
    if build_stage == "battery_holder":
        return _create_battery_holder(document, design, root, data)
    if build_stage == "cover_and_modular_turret":
        return _create_cover_and_modular_turret(document, design, root, data)

    lower = data["chassis"]["lower_deck"]
    upper = data["chassis"]["upper_deck"]
    motor_hole = data["cable_holes"]["motor_hole"]
    turret_hole = data["cable_holes"]["turret_hole"]
    lower_service_hole = data["cable_holes"].get("lower_service_hole")
    standoffs = data["base_standoffs"]
    arduino_access = data["electronics"]["arduino"]["access_openings"]
    pack_access = data["electronics"]["cannon_pcb_separate_battery_pack"]
    hull_mounting_tabs = data["hull_shell"]["mounting_tabs"]

    _add_user_parameter(design, "piano_inf_lunghezza", lower["length"], "mm", "Piano inferiore")
    _add_user_parameter(design, "piano_inf_larghezza", lower["width"], "mm", "Piano inferiore")
    _add_user_parameter(design, "piano_inf_spessore", lower["thickness"], "mm", "Piano inferiore")
    lower_component = _new_component(root, "01_Piano_inferiore")
    _, lower_plane = _centered_rectangle_prism(
        lower_component,
        "Piano_inferiore",
        lower["width"],
        lower["length"],
        "piano_inf_spessore",
    )

    if build_stage == "lower_deck_blank":
        lower_component.name = "01_Piano_inferiore_GREZZO_senza_fori"
        return document, design

    _add_user_parameter(design, "distanza_piani", upper["clearance_above_lower"], "mm", "Luce libera fra i piani")
    _add_user_parameter(design, "piano_sup_lunghezza", upper["length"], "mm", "Piano superiore")
    _add_user_parameter(design, "piano_sup_larghezza", upper["width"], "mm", "Piano superiore")
    _add_user_parameter(design, "piano_sup_spessore", upper["thickness"], "mm", "Piano superiore")

    if build_stage in (
        "base_with_standoffs",
        "base_with_standoffs_and_zip_slots",
        "base_with_upper_access_openings",
        "full_editable_reference_assembly",
    ):
        _add_user_parameter(design, "colonnina_diametro", standoffs["outer_diameter"], "mm", "Colonnine base")
        _add_user_parameter(design, "foro_vite_M3", standoffs["screw_hole_diameter"], "mm", "Gioco vite M3")
        _add_user_parameter(design, "colonnina_offset_bordo", standoffs["edge_inset"], "mm", "Centro colonnina dal bordo")
        _add_user_parameter(design, "dado_M3_chiave", standoffs["nut_across_flats"], "mm", "Sede esagonale dado M3")
        _add_user_parameter(design, "dado_M3_profondita", standoffs["nut_trap_depth"], "mm", "Profondita sede dado M3")

    if build_stage == "base_two_decks":
        _cut_round_hole(
            lower_component,
            lower_plane,
            motor_hole["diameter"],
            motor_hole["center_x"],
            motor_hole["center_y"],
            "piano_inf_spessore",
            "Foro_cavi_motori_DC",
        )

    upper_component = _new_component(root, "02_Piano_superiore")
    upper_z = "piano_inf_spessore + distanza_piani"
    _, upper_plane = _centered_rectangle_prism(
        upper_component,
        "Piano_superiore",
        upper["width"],
        upper["length"],
        "piano_sup_spessore",
        upper_z,
    )

    if build_stage == "two_decks_blank":
        lower_component.name = "01_Piano_inferiore_GREZZO_senza_fori"
        upper_component.name = "02_Piano_superiore_GREZZO_senza_fori"
        return document, design

    if build_stage in (
        "base_with_standoffs",
        "base_with_standoffs_and_zip_slots",
        "base_with_upper_access_openings",
        "full_editable_reference_assembly",
    ):
        inset = standoffs["edge_inset"]
        x_position = upper["width"] / 2.0 - inset
        y_position = upper["length"] / 2.0 - inset
        positions = (
            (-x_position, -y_position),
            (x_position, -y_position),
            (x_position, y_position),
            (-x_position, y_position),
        )

        lower_component.name = "01_Piano_inferiore_con_colonnine_M3"
        standoff_plane = _offset_plane(lower_component, "piano_inf_spessore")
        nut_plane_expression = (
            "piano_inf_spessore + distanza_piani - dado_M3_profondita"
        )
        nut_plane = _offset_plane(lower_component, nut_plane_expression)

        if build_stage in (
            "base_with_standoffs_and_zip_slots",
            "base_with_upper_access_openings",
            "full_editable_reference_assembly",
        ):
            mounting = data["chassis_mounting"]
            slot_dimensions = mounting["slot_dimensions"]
            slot_positions = mounting["slot_positions"]
            if len(slot_positions) != 4:
                raise RuntimeError(
                    "Sono richieste esattamente quattro asole per le fascette."
                )
            _add_user_parameter(
                design,
                "asola_fascetta_lunghezza",
                slot_dimensions["length"],
                "mm",
                "Asola fascetta, asse Est-Ovest",
            )
            _add_user_parameter(
                design,
                "asola_fascetta_larghezza",
                slot_dimensions["width"],
                "mm",
                "Asola fascetta, asse Sud-Nord",
            )
            for slot_index, slot in enumerate(slot_positions, start=1):
                east_west = slot.get("east_west")
                north_from_south = slot.get("north_from_south_edge")
                if not isinstance(east_west, (int, float)) or not isinstance(
                    north_from_south, (int, float)
                ):
                    raise RuntimeError(
                        "Ogni asola deve avere coordinate numeriche "
                        "east_west e north_from_south_edge."
                    )
                if north_from_south <= 0 or north_from_south >= lower["length"]:
                    raise RuntimeError(
                        "Le quote Nord delle asole devono rimanere entro il "
                        "piano inferiore."
                    )
                center_y = -lower["length"] / 2.0 + north_from_south
                _cut_rectangle(
                    lower_component,
                    lower_plane,
                    slot_dimensions["length"],
                    slot_dimensions["width"],
                    east_west,
                    center_y,
                    "piano_inf_spessore",
                    f"Asola_fascetta_{slot_index:02d}",
                )

            if build_stage in (
                "base_with_upper_access_openings",
                "full_editable_reference_assembly",
            ):
                _add_user_parameter(
                    design,
                    "foro_servizio_inferiore_larghezza",
                    lower_service_hole["width"],
                    "mm",
                    "Foro 10x10 vicino Arduino",
                )
                _add_user_parameter(
                    design,
                    "foro_servizio_inferiore_lunghezza",
                    lower_service_hole["length"],
                    "mm",
                    "Foro 10x10 vicino Arduino",
                )
                _add_user_parameter(
                    design,
                    "foro_servizio_inferiore_centro_x",
                    lower_service_hole["center_x"],
                    "mm",
                    "Centro quasi sull'asse del carro",
                )
                _add_user_parameter(
                    design,
                    "foro_servizio_inferiore_da_sud",
                    lower_service_hole["north_from_south_edge"],
                    "mm",
                    "20 mm oltre il centro dell'ultima asola fascetta",
                )
                _cut_rectangle(
                    lower_component,
                    lower_plane,
                    lower_service_hole["width"],
                    lower_service_hole["length"],
                    lower_service_hole["center_x"],
                    lower_service_hole["center_y"],
                    "piano_inf_spessore",
                    "Foro_servizio_10x10_vicino_Arduino",
                )

        for index, (center_x, center_y) in enumerate(positions, start=1):
            label = f"{index:02d}"
            _cut_round_hole(
                upper_component,
                upper_plane,
                standoffs["screw_hole_diameter"],
                center_x,
                center_y,
                "piano_sup_spessore",
                f"Foro_M3_superiore_{label}",
            )
            _cylinder_prism(
                lower_component,
                standoff_plane,
                f"Colonnina_M3_{label}",
                standoffs["outer_diameter"],
                center_x,
                center_y,
                "distanza_piani",
                adsk.fusion.FeatureOperations.JoinFeatureOperation,
            )
            _cut_round_hole(
                lower_component,
                lower_plane,
                standoffs["screw_hole_diameter"],
                center_x,
                center_y,
                "piano_inf_spessore + distanza_piani",
                f"Foro_passante_M3_colonnina_{label}",
            )
            _cut_hex_pocket(
                lower_component,
                nut_plane,
                standoffs["nut_across_flats"],
                center_x,
                center_y,
                "dado_M3_profondita",
                f"Sede_dado_M3_{label}",
            )

        if build_stage in (
            "base_with_upper_access_openings",
            "full_editable_reference_assembly",
        ):
            openings = (
                {
                    "name": "Arduino_25x25",
                    "width": arduino_access["width"],
                    "length": arduino_access["length"],
                    "center_x": arduino_access["center_x"],
                    "center_y": arduino_access["center_y"],
                },
                {
                    "name": "pacco_batteria_PCB_cannone_60x33",
                    "width": pack_access["opening_width"],
                    "length": pack_access["opening_length"],
                    "center_x": pack_access["opening_center_x"],
                    "center_y": pack_access["opening_center_y"],
                },
            )
            _validate_upper_access_openings(upper, standoffs, openings)

            _add_user_parameter(
                design,
                "apertura_arduino_larghezza",
                arduino_access["width"],
                "mm",
                "Apertura superiore sopra Arduino",
            )
            _add_user_parameter(
                design,
                "apertura_arduino_lunghezza",
                arduino_access["length"],
                "mm",
                "Apertura superiore sopra Arduino",
            )
            _add_user_parameter(
                design,
                "apertura_arduino_centro_x",
                arduino_access["center_x"],
                "mm",
                "Centro Est-Ovest apertura Arduino",
            )
            _add_user_parameter(
                design,
                "apertura_arduino_centro_y",
                arduino_access["center_y"],
                "mm",
                "Centro Sud-Nord apertura Arduino",
            )
            _add_user_parameter(
                design,
                "apertura_pacco_batteria_larghezza",
                pack_access["opening_width"],
                "mm",
                "Apertura superiore pacco batteria PCB cannone",
            )
            _add_user_parameter(
                design,
                "apertura_pacco_batteria_lunghezza",
                pack_access["opening_length"],
                "mm",
                "Apertura superiore pacco batteria PCB cannone",
            )
            _add_user_parameter(
                design,
                "apertura_pacco_batteria_centro_x",
                pack_access["opening_center_x"],
                "mm",
                "Centro Est-Ovest apertura pacco batteria PCB cannone",
            )
            _add_user_parameter(
                design,
                "apertura_pacco_batteria_centro_y",
                pack_access["opening_center_y"],
                "mm",
                "Centro Sud-Nord apertura pacco batteria PCB cannone",
            )

            _cut_rectangle(
                upper_component,
                upper_plane,
                arduino_access["width"],
                arduino_access["length"],
                arduino_access["center_x"],
                arduino_access["center_y"],
                "piano_sup_spessore",
                "Apertura_Arduino_25x25_D2_D7_S1_S8",
            )
            _cut_rectangle(
                upper_component,
                upper_plane,
                pack_access["opening_width"],
                pack_access["opening_length"],
                pack_access["opening_center_x"],
                pack_access["opening_center_y"],
                "piano_sup_spessore",
                "Apertura_pacco_batteria_PCB_cannone_60x33",
            )

            if build_stage == "full_editable_reference_assembly":
                _add_user_parameter(
                    design,
                    "foro_piano_superiore_M2_5_guscio",
                    hull_mounting_tabs["upper_deck_clearance_hole_diameter"],
                    "mm",
                    "Quattro viti M2.5x8 per trattenere il guscio inferiore",
                )
                for index, tab in enumerate(
                    hull_mounting_tabs["positions"], start=1
                ):
                    _cut_round_hole(
                        upper_component,
                        upper_plane,
                        hull_mounting_tabs[
                            "upper_deck_clearance_hole_diameter"
                        ],
                        tab["x"],
                        tab["y"],
                        "piano_sup_spessore",
                        f"Foro_M2_5_guscio_inferiore_{index:02d}_{tab['name']}",
                    )

                # Il piano superiore resta strutturalmente intero al centro.
                # Dopo l'anello nel tetto, l'ansa viene guidata nel vano da
                # 30 mm e scende dall'apertura Arduino 25 x 25 mm gia creata.

        if build_stage == "full_editable_reference_assembly":
            _integrate_battery_holder_into_lower_deck(
                design,
                lower_component,
                data,
            )
            _create_full_reference_subassemblies(
                document,
                design,
                root,
                data,
            )

        if build_stage == "full_editable_reference_assembly":
            lower_component.bRepBodies.item(0).name = (
                "Piano_inferiore_colonnine_M3_supporto_batteria_integrato"
            )
        else:
            lower_component.bRepBodies.item(0).name = (
                "Piano_inferiore_con_colonnine_M3"
            )
        return document, design

    _cut_round_hole(
        upper_component,
        upper_plane,
        turret_hole["diameter"],
        turret_hole["center_x"],
        turret_hole["center_y"],
        "piano_sup_spessore",
        "Foro_cavi_torretta",
    )

    return document, design


def _export(design, build_stage):
    os.makedirs(EXCHANGE_DIR, exist_ok=True)
    export_manager = design.exportManager
    if build_stage == "lower_deck_blank":
        stem = "piano_inferiore_grezzo_senza_fori"
    elif build_stage == "two_decks_blank":
        stem = "base_due_piani_grezza_senza_fori"
    elif build_stage == "base_with_standoffs":
        stem = "base_colonnine_integrate_dadi_M3_senza_passacavi"
    elif build_stage == "base_with_standoffs_and_zip_slots":
        stem = "base_colonnine_M3_asole_fascette_senza_passacavi"
    elif build_stage == "base_with_upper_access_openings":
        stem = "base_colonnine_M3_asole_aperture_superiori_Arduino_pacco_batteria"
    elif build_stage == "full_editable_reference_assembly":
        stem = (
            "carro_armato_assieme_completo_modificabile_"
            "v5_cinematica_stepper_servo_M2_5"
        )
    elif build_stage == "battery_holder":
        stem = "supporto_batteria_standalone_parametrico_v2_apertura_utile_10mm"
    elif build_stage == "cover_and_modular_turret":
        stem = "torretta_modulare_stampabile_v6_doppia_D_5x3x6"
    else:
        stem = "carro_armato_parametrico"
    f3d_path = os.path.join(EXCHANGE_DIR, f"{stem}.f3d")
    step_path = os.path.join(EXCHANGE_DIR, f"{stem}.step")

    f3d_options = export_manager.createFusionArchiveExportOptions(f3d_path)
    if not export_manager.execute(f3d_options):
        raise RuntimeError("Esportazione F3D non riuscita")

    step_options = export_manager.createSTEPExportOptions(step_path)
    if not export_manager.execute(step_options):
        raise RuntimeError("Esportazione STEP non riuscita")

    return f3d_path, step_path


def run(_context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        data = _read_parameters()
        build_stage = data.get("meta", {}).get("build_stage")
        if build_stage not in (
            "lower_deck_blank",
            "two_decks_blank",
            "base_with_standoffs",
            "base_with_standoffs_and_zip_slots",
            "base_with_upper_access_openings",
            "full_editable_reference_assembly",
            "base_two_decks",
            "battery_holder",
            "cover_and_modular_turret",
        ):
            ui.messageBox(
                "Generazione interrotta: meta.build_stage deve essere "
                "'lower_deck_blank', 'two_decks_blank', "
                "'base_with_standoffs', "
                "'base_with_standoffs_and_zip_slots', "
                "'base_with_upper_access_openings', "
                "'full_editable_reference_assembly', 'base_two_decks' oppure "
                "'battery_holder' oppure 'cover_and_modular_turret'.",
                "Tank Generator",
            )
            return

        if build_stage == "lower_deck_blank":
            required_values = REQUIRED_LOWER_BLANK_VALUES
        elif build_stage == "two_decks_blank":
            required_values = REQUIRED_TWO_DECK_BLANK_VALUES
        elif build_stage == "base_with_standoffs":
            required_values = REQUIRED_STANDOFF_VALUES
        elif build_stage == "base_with_standoffs_and_zip_slots":
            required_values = REQUIRED_ZIP_SLOT_VALUES
        elif build_stage == "base_with_upper_access_openings":
            required_values = REQUIRED_UPPER_ACCESS_VALUES
        elif build_stage == "full_editable_reference_assembly":
            required_values = REQUIRED_FULL_REFERENCE_ASSEMBLY_VALUES
        elif build_stage == "battery_holder":
            required_values = REQUIRED_BATTERY_HOLDER_VALUES
        elif build_stage == "cover_and_modular_turret":
            required_values = REQUIRED_COVER_TURRET_VALUES
        else:
            required_values = REQUIRED_BASE_VALUES

        missing = _missing_values(data, required_values)
        if missing:
            ui.messageBox(
                "Generazione interrotta: mancano quote confermate.\n\n- "
                + "\n- ".join(missing),
                "Tank Generator",
            )
            return

        positive_paths = tuple(
            path
            for path in required_values
            if not path.endswith("center_x")
            and not path.endswith("center_y")
            and not path.endswith(".kind")
            and not path.endswith(".opening_end")
            and not path.endswith(".long_wall_side")
            and path != "turret.cable_routing.azimuth_arc_start_deg"
        )
        invalid = _validate_positive(data, positive_paths)
        if invalid:
            ui.messageBox(
                "Generazione interrotta: queste quote devono essere numeri positivi.\n\n- "
                + "\n- ".join(invalid),
                "Tank Generator",
            )
            return

        _, design = _create_design(data)
        f3d_path, step_path = _export(design, build_stage)
        app.activeViewport.fit()
        ui.messageBox(
            "Modello generato ed esportato.\n\n"
            f"F3D: {f3d_path}\nSTEP: {step_path}",
            "Tank Generator",
        )
    except Exception:
        if ui:
            ui.messageBox("Errore durante la generazione:\n\n" + traceback.format_exc())


def stop(_context):
    return
