# Lab 6: Nav2 Navigation Stack Tuning

## Overview

This laboratory work involved tuning the parameters of the Nav2 navigation stack for a TurtleBot3 (Burger model) robot in a simulated Gazebo environment. 
The initial settings in the `nav2_params.yaml` file contained intentional errors and suboptimal values, causing the robot to lose localization, fail to build safe paths, generate "ghost" obstacles, and move erratically.

**Objective:** Analyze the robot's behavior in RViz and Gazebo and calibrate the localization parameters (AMCL), local/global costmaps, and the controller (DWB Local Planner).

## What We Changed and Why (Parameter Analysis)

All changes were made in the `nav2_params.yaml` file. Below is a detailed breakdown of the tuned modules.

### 1. Localization (`amcl`)

The AMCL algorithm is responsible for the robot's understanding of its position on the map (the green particle cloud in RViz). The initial parameters forced the robot to constantly doubt its sensors, leading to a catastrophic accumulation of error (drift).

* **`z_hit`** (changed from `0.5` to `0.7`): The weight of a "successful" lidar measurement. We increased the robot's trust in its laser rangefinder. Now it is 70% confident that it sees a real wall, not just random noise.
* **`z_rand`** (changed from `0.5` to `0.3`): The weight of random noise. We decreased the probability of the robot ignoring correct data. Thanks to this pair of parameters, the red lidar dots in RViz perfectly "stuck" to the global map, eliminating drift.
* **`max_particles` / `min_particles`** (changed from `2000/500` to `1000/250`): Since the room is relatively small (8x8 m), 2000 hypotheses (particles) unnecessarily overloaded the processor. Reducing the amount allowed the algorithm to "compress" the point cloud faster without losing localization accuracy.

### 2. Costmaps: `local_costmap` and `global_costmap`

These modules dictate how the robot perceives obstacles. The initial settings turned the map into "Minecraft" with giant pixels and impassable zones.

* **`resolution`** (changed from `0.2` to `0.05`): Map resolution (meters per cell). This change allowed the local costmap to match the detailing of the static map. Instead of rough 20x20 cm squares, the robot started seeing accurate obstacle contours with a 5 cm detailing. This is critical for navigating through narrow passages.
* **`inflation_radius`** (changed from `1.0` to `0.3`): The radius of the "danger aura" around walls. The initial 1 meter forced the robot to consider half of the room a deadly zone and blocked path generation. Reducing it to 30 cm (slightly more than the robot's physical radius) allowed the planner to maneuver freely between blocks.
* **`update_frequency` / `publish_frequency`** (changed from `2.0/1.0` to `10.0` for `local_costmap`): Map update frequency. At 2 Hz, the local costmap could not keep up with the robot's turns (smearing effect). 10 Hz provided a smooth and instantaneous reaction to dynamic changes.

### 3. Driver: `controller_server`

This module converts the path line into specific velocity commands for the wheels. The initial parameters turned the small robot into a race car that couldn't brake in time.

* **`max_vel_x`** (changed from `1.2` to `0.75`): Maximum linear velocity. 1.2 m/s is too fast for a tight indoor space.
* **`max_vel_theta`** (changed from `2.5` to `1.5`): Maximum angular velocity. Decreasing this made turns more controllable, preventing endless oscillation ("dancing" in place) when adjusting the heading.
* **`acc_lim_x`** (changed from `3.0` to `1.0`): Acceleration limit. Reducing this prevents jerks and wheel slip at the start, which also improves odometry tracking.
* **`xy_goal_tolerance`** (changed from `0.75` to `0.3`): Goal radius tolerance. The robot no longer registers a successful stop a meter before the target point; instead, it approaches the goal much more accurately.

## Conclusions

As a result of tuning the parameters, the robot's behavior improved dramatically. The issue of "ghost obstacles" (when localization failure drew non-existent walls on the local costmap) was resolved, space loss during prolonged movement (odometry drift) was eliminated, and smooth, safe navigation was achieved in an environment with densely placed obstacles.
