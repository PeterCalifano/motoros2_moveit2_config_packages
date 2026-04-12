# Dual GP12 MoveIt2 Implementation Plan

## Scope

- [ ] Keep `motoman_gp12_support` focused on reusable GP12 robot description content only.
- [ ] Keep `motoman_gp12_moveit2_config` working as the existing single-robot MoveIt package.
- [ ] Introduce a separate cell-description package for the dual GP12 + rail + target scene.
- [ ] Introduce a separate `motoman_gp12_dual_moveit2_config` package for dual-robot MoveIt planning.
- [ ] Support dual GP12 in two selectable cell modes: `with_rail` and `without_rail`.

## Phase 1: Freeze The Current Baseline

- [ ] Confirm the current single-robot GP12 MoveIt flow still launches from `motoman_gp12_moveit2_config`.
- [ ] Confirm the current dual-scene RViz visualization still launches from the existing dual-scene xacro.
- [ ] Treat current files under `motoman_gp12_support/urdf/gp12_dual_rail*.xacro` as the behavior baseline for the new cell package.
- [ ] Decide the final package name for the cell description package.
- [ ] Decide the external configuration interface for cell topology selection, for example `cell_mode:=rail|fixed` or `with_rail:=true|false`.
- [ ] Decide whether generated `.urdf` files will continue to be committed or regenerated only when needed.

## Phase 2: Create A Dedicated Cell Description Package

- [ ] Create a new package for facility-specific scene composition, for example `motoman_gp12_dual_cell_support`.
- [ ] Add `CMakeLists.txt` install rules for `launch`, `urdf`, and any `config` directories in the new package.
- [ ] Add `package.xml` dependencies on `motoman_gp12_support`, `cosmica_resources`, `motoman_resources`, `xacro`, `robot_state_publisher`, `joint_state_publisher_gui`, and `rviz2`.
- [ ] Move the dual-scene launch currently in `cosmica_resources/launch/view_gp12_dual_rail_target.launch.xml` into the new cell package.
- [ ] Move the top-level dual-scene xacro composition out of `motoman_gp12_support` and into the new cell package.
- [ ] Leave `cosmica_resources` responsible for target meshes and target-only reusable description assets, not full robot-cell launches.
- [ ] Leave `motoman_gp12_support` responsible for the GP12 robot macro and GP12-only viewer launches, not facility-specific cell assembly.

## Phase 3: Extract Reusable Scene Macros

- [ ] Create a reusable rail macro, for example `urdf/linear_rail_macro.xacro`, that owns the rail link, geometry, and prismatic joint definition.
- [ ] Create a reusable fixed-mount macro, for example `urdf/fixed_mount_macro.xacro`, that inserts a named mount frame between a parent link and a mounted object.
- [ ] Replace the placeholder `cosmica_resources/urdf/itokawa_target.xacro` with a usable target macro that owns only the target link geometry and scale.
- [ ] Remove inline target geometry from the current dual-scene xacro and instantiate the reusable target macro instead.
- [ ] Remove inline rail geometry from the current dual-scene xacro and instantiate the reusable rail macro instead.
- [ ] Keep the GP12 robot itself instantiated through `motoman_gp12_support/urdf/gp12_macro.xacro`.

## Phase 4: Parameterize Cell Layout Data

- [ ] Replace hard-coded rail dimensions with named xacro args or properties.
- [ ] Replace hard-coded world-to-rail placement with named xacro args or properties.
- [ ] Replace hard-coded robot placement transforms with named xacro args or properties.
- [ ] Replace hard-coded target mount translation and rotation with named xacro args or properties.
- [ ] Replace hard-coded target scale with a named xacro arg or property.
- [ ] Add a top-level configuration switch that selects whether `group_1` is rail-mounted or fixed directly to `world`.
- [ ] Decide whether calibration values live directly in the top-level xacro or in a dedicated YAML-backed config workflow.
- [ ] Document the canonical transform chain for the mounted target.

## Phase 5: Compose The Top-Level Dual Cell Description

- [ ] Create a top-level cell xacro in the new package, for example `urdf/gp12_dual_cell.xacro`.
- [ ] Instantiate `group_1/` and `group_2/` GP12 robots using `motoman_gp12`.
- [ ] In rail mode, attach `group_1/base_link` to the rail through `rail_joint`.
- [ ] In fixed mode, attach `group_1/base_link` directly to `world` through a fixed transform.
- [ ] Attach `group_2/base_link` to `world` through a fixed transform.
- [ ] Attach the target to an explicit mount frame on `group_2`.
- [ ] Decide whether the mount parent should be `group_2/flange` or `group_2/tool0`, and keep that choice consistent across the stack.
- [ ] Keep `world` as the top-level fixed frame for the full cell.
- [ ] Generate the expanded URDF from the new top-level xacro if the repo continues to track generated URDF artifacts.
- [ ] Verify the top-level cell xacro can expand cleanly in both rail and fixed-base modes.

## Phase 6: Create `motoman_gp12_dual_moveit2_config`

- [ ] Create a new MoveIt package named `motoman_gp12_dual_moveit2_config`.
- [ ] Point its robot description at the new dual-cell xacro and make the selected cell mode configurable at launch.
- [ ] Create distinct semantic/config variants for rail and fixed-base modes where topology differs.
- [ ] Do not edit the single-robot SRDF in place; create dual-stack assets from the dual-cell URDF variants.
- [ ] Keep the existing single-robot `motoman_gp12_moveit2_config` unchanged except for shared fixes that are truly common.
- [ ] Add package dependencies required for MoveIt launch, RViz, xacro processing, and the new cell package.

## Phase 7: Define MoveIt Semantics For The Dual Cell

- [ ] Create a planning group for `group_1` from `group_1/base_link` to `group_1/tool0`.
- [ ] Create a planning group for `group_2` from `group_2/base_link` to `group_2/tool0`.
- [ ] Create a planning group that includes `rail_joint` plus the `group_1` arm joints if rail-aware planning is required.
- [ ] Create a fixed-base semantic variant that omits `rail_joint` anywhere it does not exist in the selected robot description.
- [ ] Create a combined planning group or subgroup structure for coordinated dual-arm planning if the use case requires it.
- [ ] Add named group states such as `home` for each arm and any dual-arm composite states that are operationally useful.
- [ ] Regenerate the self-collision matrix separately for each supported topology if the rail and fixed-base scenes differ structurally.
- [ ] Review and trim any false-positive or over-permissive collision disables introduced by automatic generation.

## Phase 8: Update Kinematics, Joint Limits, And Controllers

- [ ] Add kinematics entries for both arm planning groups in `kinematics.yaml`.
- [ ] Add rail-aware kinematics strategy if a rail-inclusive group is expected to plan through MoveIt.
- [ ] Extend `joint_limits.yaml` to include `rail_joint`, `group_1/joint_1..6`, and `group_2/joint_1..6`.
- [ ] Define the controller strategy for the dual stack.
- [ ] Decide whether the production controller model is one action server per robot, a combined controller abstraction, or visualization-only stubs during early integration.
- [ ] Provide mode-specific controller and joint-limit config where the rail-enabled and fixed-base joint lists differ.
- [ ] Ensure action namespaces match the MotoROS2 deployment model instead of relying on single-robot defaults.

## Phase 9: Update Launch Files

- [ ] Create a dual-stack `demo.launch.py` in `motoman_gp12_dual_moveit2_config`.
- [ ] Ensure the dual launch selects the correct robot description, SRDF, kinematics, controllers, and RViz config based on the chosen cell mode.
- [ ] Keep `robot_state_publisher` and `move_group` pointed at the same robot description source.
- [ ] Add a dual-cell RViz config that displays both manipulators, the rail, and the mounted target cleanly.
- [ ] Keep the current single-robot `demo.launch.py` intact for existing workflows.

## Phase 10: Define Joint-State Integration

- [ ] Define the canonical joint list for rail mode as `rail_joint`, `group_1/joint_1..6`, and `group_2/joint_1..6`.
- [ ] Define the canonical joint list for fixed-base mode as `group_1/joint_1..6` and `group_2/joint_1..6`.
- [ ] Decide whether the immediate target is visualization-only, simulated planning, or live MotoROS2-backed execution.
- [ ] If live data is required, define how upstream state is converted into one coherent `sensor_msgs/msg/JointState` stream.
- [ ] Decide how rail state is sourced in production if the rail is not published by the same controller as the GP12 arms.
- [ ] Validate that joint names in live topics exactly match the URDF, SRDF, and controller config.

## Phase 11: Validation And Regression Checks

- [ ] Add a repeatable xacro expansion check for the new top-level cell xacro.
- [ ] Add a repeatable xacro expansion check for the new dual MoveIt robot description xacro.
- [ ] Launch the new cell viewer and confirm `world`, rail, both robots, and target frames render correctly.
- [ ] Launch the new dual MoveIt demo and confirm both arm groups appear in RViz.
- [ ] Confirm the rail-inclusive group appears only if intentionally configured.
- [ ] Confirm fixed-base mode launches without any references to `rail_joint` in the active semantic and controller configuration.
- [ ] Confirm the target mount frame lands where expected relative to `group_2/flange` or `group_2/tool0`.
- [ ] Confirm the collision matrix does not block obvious valid motions or ignore obvious invalid collisions.
- [ ] Confirm the existing single-robot GP12 MoveIt demo still launches without regression.

## Phase 12: Documentation And Cleanup

- [ ] Update `README.md` to distinguish single-robot MoveIt support from the dual-cell visualization and the dual-robot MoveIt stack.
- [ ] Update usage docs to point operators at the correct launch files for single-robot MoveIt, dual-scene visualization, and dual MoveIt.
- [ ] Fix helper scripts so their names match their real behavior.
- [ ] Document where rail geometry, mount transforms, and target scale are defined.
- [ ] Document the expected controller and joint-state interfaces for future live integration.
- [ ] Remove or archive obsolete dual-scene files from `motoman_gp12_support` and `cosmica_resources` once the new package is in place.

## Exit Criteria

- [ ] `motoman_gp12_support` contains reusable GP12 robot description content only.
- [ ] The cell-specific dual-scene description lives in its own package.
- [ ] Rail and target mounting are reusable macros with parameterized transforms.
- [ ] `motoman_gp12_dual_moveit2_config` exists and launches against the dual-cell description.
- [ ] The dual stack can be launched in both rail-enabled and fixed-base modes through configuration.
- [ ] The dual MoveIt package exposes the required planning groups and joint lists.
- [ ] The single-robot GP12 MoveIt package still works unchanged for current users.
