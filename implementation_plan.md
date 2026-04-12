# Dual GP12 MoveIt2 Implementation Plan

## Scope

- [x] Keep `motoman_gp12_support` focused on reusable GP12 robot description content only.
- [x] Keep `motoman_gp12_moveit2_config` working as the existing single-robot MoveIt package.
- [x] Introduce a separate cell-description package for the dual GP12 + rail + target scene.
- [x] Introduce a separate `motoman_gp12_dual_moveit2_config` package for dual-robot MoveIt planning.
- [x] Support dual GP12 in two selectable cell modes: `rail` and `fixed`.

## Phase 1: Freeze The Current Baseline

- [x] Confirm the current single-robot GP12 MoveIt package remains the reference single-robot stack.
- [x] Confirm the current dual-scene RViz visualization still launches from the existing dual-scene xacro.
- [x] Treat current files under `motoman_gp12_support/urdf/gp12_dual_rail*.xacro` as the behavior baseline for the new cell package.
- [x] Decide the final package name for the cell description package.
- [x] Decide the external configuration interface for cell topology selection, for example `cell_mode:=rail|fixed` or `with_rail:=true|false`.
- [x] Decide whether generated `.urdf` files will continue to be committed or regenerated only when needed.

### Phase 1 Outcomes

- [x] Validate the current single-robot GP12 package by expanding `motoman_gp12_moveit2_config/config/motoman_gp12.urdf.xacro` and preserving the existing package layout.
- [x] Validate the current dual-scene entrypoint by resolving `cosmica_resources/view_gp12_dual_rail_target.launch.xml` and expanding `motoman_gp12_support/urdf/gp12_dual_rail_tool.xacro`.
- [x] Use `motoman_gp12_dual_cell_support` as the new cell-description package name.
- [x] Use `cell_mode:=rail|fixed` as the external topology-selection interface.
- [x] Keep generated `.urdf` files committed for consistency with current repository conventions, but treat xacro as the source of truth and avoid manual edits to generated URDF artifacts.

## Phase 2: Create A Dedicated Cell Description Package

- [x] Create a new package for facility-specific scene composition, for example `motoman_gp12_dual_cell_support`.
- [x] Add `CMakeLists.txt` install rules for `launch`, `urdf`, and any `config` directories in the new package.
- [x] Add `package.xml` dependencies on `motoman_gp12_support`, `cosmica_resources`, `motoman_resources`, `xacro`, `robot_state_publisher`, `joint_state_publisher_gui`, and `rviz2`.
- [x] Move the dual-scene launch currently in `cosmica_resources/launch/view_gp12_dual_rail_target.launch.xml` into the new cell package.
- [x] Move the top-level dual-scene xacro composition out of `motoman_gp12_support` and into the new cell package.
- [x] Leave `cosmica_resources` responsible for target meshes and target-only reusable description assets, not full robot-cell launches.
- [x] Leave `motoman_gp12_support` responsible for the GP12 robot macro and GP12-only viewer launches, not facility-specific cell assembly.

### Phase 2 Interim Status

- [x] Seed the new package with baseline dual-scene launch and xacro files so the new package can build and resolve in isolation.
- [x] Build `motoman_gp12_dual_cell_support` successfully with `colcon build --packages-select motoman_gp12_dual_cell_support`.
- [x] Validate the new package launch entrypoint resolves with `ros2 launch motoman_gp12_dual_cell_support view_gp12_dual_rail_target.launch.xml --show-args`.

## Phase 3: Extract Reusable Scene Macros

- [x] Create a reusable rail macro, for example `urdf/linear_rail_macro.xacro`, that owns the rail link, geometry, and prismatic joint definition.
- [x] Create a reusable fixed-mount macro, for example `urdf/fixed_mount_macro.xacro`, that inserts a named mount frame between a parent link and a mounted object.
- [x] Replace the placeholder `cosmica_resources/urdf/itokawa_target.xacro` with a usable target macro that owns only the target link geometry and scale.
- [x] Remove inline target geometry from the current dual-scene xacro and instantiate the reusable target macro instead.
- [x] Remove inline rail geometry from the current dual-scene xacro and instantiate the reusable rail macro instead.
- [x] Keep the GP12 robot itself instantiated through `motoman_gp12_support/urdf/gp12_macro.xacro`.

## Phase 4: Parameterize Cell Layout Data

- [x] Replace hard-coded rail dimensions with named xacro args or properties.
- [x] Replace hard-coded world-to-rail placement with named xacro args or properties.
- [x] Replace hard-coded robot placement transforms with named xacro args or properties.
- [x] Replace hard-coded target mount translation and rotation with named xacro args or properties.
- [x] Replace hard-coded target scale with a named xacro arg or property.
- [x] Add a top-level configuration switch that selects whether `group_1` is rail-mounted or fixed directly to `world`.
- [x] Decide whether calibration values live directly in the top-level xacro or in a dedicated YAML-backed config workflow.
- [x] Document the canonical transform chain for the mounted target.

## Phase 5: Compose The Top-Level Dual Cell Description

- [x] Create a top-level cell xacro in the new package, for example `urdf/gp12_dual_cell.xacro`.
- [x] Instantiate `group_1/` and `group_2/` GP12 robots using `motoman_gp12`.
- [x] In rail mode, attach `group_1/base_link` to the rail through `rail_joint`.
- [x] In fixed mode, attach `group_1/base_link` directly to `world` through a fixed transform.
- [x] Attach `group_2/base_link` to `world` through a fixed transform.
- [x] Attach the target to an explicit mount frame on `group_2`.
- [x] Decide whether the mount parent should be `group_2/flange` or `group_2/tool0`, and keep that choice consistent across the stack.
- [x] Keep `world` as the top-level fixed frame for the full cell.
- [x] Validate expanded URDF generation from the new top-level xacro.
- [x] Verify the top-level cell xacro can expand cleanly in both rail and fixed-base modes.

## Phase 6: Create `motoman_gp12_dual_moveit2_config`

- [x] Create a new MoveIt package named `motoman_gp12_dual_moveit2_config`.
- [x] Point its robot description at the new dual-cell xacro and make the selected cell mode configurable at launch.
- [x] Create distinct semantic/config variants for rail and fixed-base modes where topology differs.
- [x] Do not edit the single-robot SRDF in place; create dual-stack assets from the dual-cell URDF variants.
- [x] Keep the existing single-robot `motoman_gp12_moveit2_config` unchanged except for shared fixes that are truly common.
- [x] Add package dependencies required for MoveIt launch, RViz, xacro processing, and the new cell package.

## Phase 7: Define MoveIt Semantics For The Dual Cell

- [x] Create a planning group for `group_1` from `group_1/base_link` to `group_1/tool0`.
- [x] Create a planning group for `group_2` from `group_2/base_link` to `group_2/tool0`.
- [x] Create a planning group that includes `rail_joint` plus the `group_1` arm joints if rail-aware planning is required.
- [x] Create a fixed-base semantic variant that omits `rail_joint` anywhere it does not exist in the selected robot description.
- [x] Create a combined planning group or subgroup structure for coordinated dual-arm planning if the use case requires it.
- [x] Add named group states such as `home` for each arm and any dual-arm composite states that are operationally useful.
- [x] Finalize separate self-collision disable baselines for the rail and fixed-base topologies.
- [x] Review and trim redundant or nonfunctional collision disables in those SRDF variants.

### Phase 7 Interim Status

- [x] Add hand-authored collision disables for both arm variants so the dual SRDFs are usable before automated collision-matrix generation.
- [x] Complete a manual review pass to remove redundant disables tied to collisionless fixed-joint links such as `flange`, `tool0`, and `target_mount`.
- [x] Record automated collision-matrix generation with the MoveIt Setup Assistant or equivalent tooling as a later validation step instead of a phase-7 implementation blocker.

## Phase 8: Update Kinematics, Joint Limits, And Controllers

- [x] Add kinematics entries for both arm planning groups in `kinematics.yaml`.
- [x] Add rail-aware kinematics strategy if a rail-inclusive group is expected to plan through MoveIt.
- [x] Extend `joint_limits.yaml` to include `rail_joint`, `group_1/joint_1..6`, and `group_2/joint_1..6`.
- [x] Define the controller strategy for the dual stack.
- [x] Decide whether the production controller model is one action server per robot, a combined controller abstraction, or visualization-only stubs during early integration.
- [x] Provide mode-specific controller and joint-limit config where the rail-enabled and fixed-base joint lists differ.
- [x] Ensure action namespaces match the MotoROS2 deployment model instead of relying on single-robot defaults.

## Phase 9: Update Launch Files

- [x] Create a dual-stack `demo.launch.py` in `motoman_gp12_dual_moveit2_config`.
- [x] Ensure the dual launch selects the correct robot description, SRDF, kinematics, controllers, and RViz config based on the chosen cell mode.
- [x] Keep `robot_state_publisher` and `move_group` pointed at the same robot description source.
- [x] Add a dual-cell RViz config that displays both manipulators, the rail, and the mounted target cleanly.
- [x] Keep the current single-robot `demo.launch.py` intact for existing workflows.

## Phase 10: Define Joint-State Integration

- [x] Define the canonical joint list for rail mode as `rail_joint`, `group_1/joint_1..6`, and `group_2/joint_1..6`.
- [x] Define the canonical joint list for fixed-base mode as `group_1/joint_1..6` and `group_2/joint_1..6`.
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

## Phase 13: Mesh-Derived Collision Utility

- [ ] Add a Python utility that accepts a user-supplied STL or OBJ and derives simplified collision geometry from it.
- [ ] Support at minimum primitive fitting modes for `box`, `sphere`, and `cylinder`.
- [ ] Support a configurable margin scale such as `1.05` so collision proxies can be conservatively expanded.
- [ ] Output derived dimensions, offsets, and orientation in a machine-readable format such as YAML.
- [ ] Add an output mode that emits a URDF or xacro-ready collision snippet for direct integration.
- [ ] Preserve the mesh-frame to collision-frame offset so generated collision geometry stays aligned with the visual mesh origin.
- [ ] Optionally support an oriented bounding box mode if axis-aligned boxes are too loose for irregular meshes.
- [ ] Optionally support simplified collision-mesh generation such as convex hull or decimated mesh export for targets that do not fit primitives well.
- [ ] Document recommended Python dependencies for the utility, for example `trimesh`, `numpy`, and any optional mesh-processing libraries.
- [ ] Add at least one example workflow showing how to derive collision geometry for a target mesh and store the result in package config.

## Exit Criteria

- [x] `motoman_gp12_support` contains reusable GP12 robot description content only.
- [x] The cell-specific dual-scene description lives in its own package.
- [x] Rail and target mounting are reusable macros with parameterized transforms.
- [ ] `motoman_gp12_dual_moveit2_config` exists and launches against the dual-cell description.
- [x] The dual stack can be launched in both rail-enabled and fixed-base modes through configuration.
- [x] The dual MoveIt package exposes the required planning groups and joint lists.
- [ ] The single-robot GP12 MoveIt package still works unchanged for current users.
- [ ] The workspace includes a utility workflow for deriving simplified collision geometry from user-supplied STL or OBJ assets.
