import numpy as np
import matplotlib.pyplot as plt


# =====================================================================
# 1. PHYSICAL DIMENSIONS & COMPOSITE WALL GRID
# =====================================================================

dx = 0.005  # Spatial step: 5 mm

thickness_out_plaster = 0.02  # 20 mm
thickness_core = 0.15         # 150 mm
thickness_in_plaster = 0.02   # 20 mm

nodes_out_plaster = int(thickness_out_plaster / dx)
nodes_core = int(thickness_core / dx)
nodes_in_plaster = int(thickness_in_plaster / dx)

nx = nodes_out_plaster + nodes_core + nodes_in_plaster + 1


# Material-property profiles across the wall
k_profile = np.zeros(nx)
rho_profile = np.zeros(nx)
cp_profile = np.zeros(nx)


# Material properties
k_plaster = 0.70
rho_plaster = 1600.0
cp_plaster = 900.0

k_core = 0.60
rho_core = 1800.0
cp_core = 1000.0


# Outer plaster layer
k_profile[:nodes_out_plaster] = k_plaster
rho_profile[:nodes_out_plaster] = rho_plaster
cp_profile[:nodes_out_plaster] = cp_plaster

# Mud core
k_profile[nodes_out_plaster:nodes_out_plaster + nodes_core] = k_core
rho_profile[nodes_out_plaster:nodes_out_plaster + nodes_core] = rho_core
cp_profile[nodes_out_plaster:nodes_out_plaster + nodes_core] = cp_core

# Inner plaster layer
k_profile[nodes_out_plaster + nodes_core:] = k_plaster
rho_profile[nodes_out_plaster + nodes_core:] = rho_plaster
cp_profile[nodes_out_plaster + nodes_core:] = cp_plaster


# Harmonic-mean conductivities at material interfaces
k_left_arr = (
    2 * k_profile[1:-1] * k_profile[:-2]
    / (k_profile[1:-1] + k_profile[:-2])
)

k_right_arr = (
    2 * k_profile[1:-1] * k_profile[2:]
    / (k_profile[1:-1] + k_profile[2:])
)


# =====================================================================
# 2. SYNTHETIC BHUJ SUMMER CLIMATE PROFILE
# =====================================================================

np.random.seed(42)

# Five days of hourly climate input
hourly_times = np.arange(0, 120)


# Idealised daily temperature cycle
base_diurnal = (
    33.0
    + 7.0 * np.sin((hourly_times - 10) * np.pi / 12)
)

# Slowly varying multi-day temperature component
heatwave_trend = (
    2.5 * np.sin(hourly_times * np.pi / 60)
)

# Synthetic atmospheric variability
weather_noise = np.random.normal(0, 1.2, 120)

synthetic_hourly_temperatures = (
    base_diurnal
    + heatwave_trend
    + weather_noise
)


# Synthetic wind-speed profile
base_wind = (
    4.0
    + 2.5 * np.sin((hourly_times - 12) * np.pi / 12)
)

wind_noise = np.abs(
    np.random.normal(0, 1.8, 120)
)

synthetic_hourly_winds = np.clip(
    base_wind + wind_noise,
    1.0,
    12.0
)


def get_synthetic_climate(time_in_seconds):
    """
    Return the synthetic outdoor temperature and wind speed
    corresponding to a simulation time.

    Hourly climate values are linearly interpolated to the
    one-second simulation timestep.
    """

    current_hour = time_in_seconds / 3600.0

    outdoor_temperature = np.interp(
        current_hour,
        hourly_times,
        synthetic_hourly_temperatures
    )

    wind_speed = np.interp(
        current_hour,
        hourly_times,
        synthetic_hourly_winds
    )

    # Simplified external convection coefficient
    h_outside = 5.7 + 3.8 * wind_speed

    return outdoor_temperature, h_outside


# =====================================================================
# 3. TIME STEPPING & ROOM INITIALISATION
# =====================================================================

dt = 1.0  # Time step: 1 second

days = 5
total_time = days * 24 * 3600
nt = int(total_time / dt)


# Initial wall and indoor temperatures
initial_temperature = 28.0

T_wall = np.ones(nx) * initial_temperature
T_wall_new = T_wall.copy()

T_room = initial_temperature


# Room properties
room_volume = 3.0 * 3.0 * 3.0
wall_area = 3.0 * 3.0

rho_air = 1.2
cp_air = 1005.0

room_air_mass = rho_air * room_volume

h_inside = 8.0


# Arrays for recording simulation results
time_history = np.zeros(nt)
outside_temperature_history = np.zeros(nt)
inside_temperature_history = np.zeros(nt)


# =====================================================================
# 4. TRANSIENT HEAT-TRANSFER SIMULATION
# =====================================================================

print("Running five-day composite-wall thermal simulation...")

for step in range(nt):

    current_time = step * dt

    outdoor_temperature, h_outside = (
        get_synthetic_climate(current_time)
    )


    # -----------------------------------------------------------------
    # Internal wall conduction
    # -----------------------------------------------------------------

    heat_flux_left = (
        k_left_arr
        * (T_wall[:-2] - T_wall[1:-1])
        / dx
    )

    heat_flux_right = (
        k_right_arr
        * (T_wall[1:-1] - T_wall[2:])
        / dx
    )

    T_wall_new[1:-1] = (
        T_wall[1:-1]
        + (
            dt
            / (
                rho_profile[1:-1]
                * cp_profile[1:-1]
                * dx
            )
        )
        * (heat_flux_left - heat_flux_right)
    )


    # -----------------------------------------------------------------
    # Exterior boundary
    # -----------------------------------------------------------------

    heat_flux_outside = (
        h_outside
        * (outdoor_temperature - T_wall[0])
    )

    k_interface_outside = (
        2
        * k_profile[0]
        * k_profile[1]
        / (k_profile[0] + k_profile[1])
    )

    conduction_inward = (
        k_interface_outside
        * (T_wall[1] - T_wall[0])
        / dx
    )

    T_wall_new[0] = (
        T_wall[0]
        + (
            dt
            / (
                rho_profile[0]
                * cp_profile[0]
                * (dx / 2)
            )
        )
        * (
            heat_flux_outside
            + conduction_inward
        )
    )


    # -----------------------------------------------------------------
    # Interior boundary
    # -----------------------------------------------------------------

    heat_flux_inside = (
        h_inside
        * (T_wall[-1] - T_room)
    )

    k_interface_inside = (
        2
        * k_profile[-1]
        * k_profile[-2]
        / (k_profile[-1] + k_profile[-2])
    )

    conduction_outward = (
        k_interface_inside
        * (T_wall[-2] - T_wall[-1])
        / dx
    )

    T_wall_new[-1] = (
        T_wall[-1]
        + (
            dt
            / (
                rho_profile[-1]
                * cp_profile[-1]
                * (dx / 2)
            )
        )
        * (
            conduction_outward
            - heat_flux_inside
        )
    )


    # -----------------------------------------------------------------
    # Indoor air energy balance
    # -----------------------------------------------------------------

    energy_change = (
        heat_flux_inside
        * wall_area
        * dt
    )

    T_room += (
        energy_change
        / (room_air_mass * cp_air)
    )


    # Update wall temperatures
    T_wall[:] = T_wall_new


    # -----------------------------------------------------------------
    # Store simulation results
    # -----------------------------------------------------------------

    time_history[step] = current_time / 3600.0

    outside_temperature_history[step] = (
        outdoor_temperature
    )

    inside_temperature_history[step] = T_room


print("Simulation complete. Generating figure...")


# =====================================================================
# 5. VISUALISATION
# =====================================================================

plt.figure(figsize=(14, 7))

plt.plot(
    time_history,
    outside_temperature_history,
    label="Outdoor temperature (synthetic Bhuj climate profile)",
    linestyle="-",
    alpha=0.45,
    linewidth=1.5
)

plt.plot(
    time_history,
    inside_temperature_history,
    label="Indoor room temperature",
    linewidth=2.5
)

plt.xlabel("Time elapsed (hours)")
plt.ylabel("Temperature (°C)")

plt.title(
    "Five-Day Thermal Response of a Composite Mud/Plaster Wall",
    fontweight="bold"
)

plt.grid(True, alpha=0.25)
plt.legend(loc="upper right")

plt.xlim(0, days * 24)

plt.tight_layout()


# Save figure for the GitHub repository
plt.savefig(
    "composite_wall_response.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()
