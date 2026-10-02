import numpy as np
import matplotlib.pyplot as plt


# ============================================================
# 1. PHYSICAL GRID
# ============================================================

wall_thickness = 0.15          # Wall thickness (m)
dx = 0.01                      # Spatial step (m)
nx = int(wall_thickness / dx) + 1


# ============================================================
# 2. MATERIAL PROPERTIES
# ============================================================

# Traditional mud / Bhunga wall
k_mud = 0.60                   # Thermal conductivity (W/m·K)
rho_mud = 1800.0               # Density (kg/m³)
cp_mud = 1000.0                # Specific heat capacity (J/kg·K)
alpha_mud = k_mud / (rho_mud * cp_mud)

# Modern concrete wall
k_concrete = 1.30              # Thermal conductivity (W/m·K)
rho_concrete = 2300.0           # Density (kg/m³)
cp_concrete = 880.0             # Specific heat capacity (J/kg·K)
alpha_concrete = k_concrete / (rho_concrete * cp_concrete)


# ============================================================
# 3. ROOM PROPERTIES
# ============================================================

room_volume = 3.0 * 3.0 * 3.0
wall_area = 3.0 * 3.0

rho_air = 1.2                  # Air density (kg/m³)
cp_air = 1005.0                # Air specific heat capacity (J/kg·K)
room_air_mass = rho_air * room_volume

h_outside = 20.0               # Exterior convection coefficient
h_inside = 8.0                 # Interior convection coefficient


# ============================================================
# 4. TIME CONFIGURATION
# ============================================================

dt = 2.0                       # Time step (s)
days = 5
total_time = days * 24 * 3600
nt = int(total_time / dt)


# ============================================================
# 5. INITIAL CONDITIONS
# ============================================================

initial_temperature = 28.0

T_wall_mud = np.ones(nx) * initial_temperature
T_wall_mud_new = T_wall_mud.copy()
T_room_mud = initial_temperature

T_wall_concrete = np.ones(nx) * initial_temperature
T_wall_concrete_new = T_wall_concrete.copy()
T_room_concrete = initial_temperature


# ============================================================
# 6. SIMPLIFIED BHUJ SUMMER TEMPERATURE MODEL
# ============================================================

def get_outside_temperature(time_in_seconds):
    """
    Generate a simplified 24-hour outdoor temperature cycle.

    This is a synthetic climate profile rather than measured
    weather data.
    """
    hour = (time_in_seconds / 3600.0) % 24

    average_temperature = 33.0
    amplitude = 7.0

    return average_temperature + amplitude * np.sin(
        (hour - 10) * np.pi / 12
    )


# ============================================================
# 7. SIMULATION
# ============================================================

print("Simulating mud vs. concrete thermal performance...")

time_history = np.zeros(nt)
outside_temperature_history = np.zeros(nt)
inside_mud_history = np.zeros(nt)
inside_concrete_history = np.zeros(nt)


for step in range(nt):

    current_time = step * dt
    outside_temperature = get_outside_temperature(current_time)

    # --------------------------------------------------------
    # MUD / BHUNGA MODEL
    # --------------------------------------------------------

    conduction_mud = (
        alpha_mud
        * dt
        / dx**2
        * (
            T_wall_mud[2:]
            - 2 * T_wall_mud[1:-1]
            + T_wall_mud[:-2]
        )
    )

    T_wall_mud_new[1:-1] = (
        T_wall_mud[1:-1] + conduction_mud
    )

    # Exterior boundary
    T_wall_mud_new[0] = (
        T_wall_mud[0]
        + alpha_mud * dt / dx**2
        * (
            2 * T_wall_mud[1]
            - 2 * T_wall_mud[0]
            + (2 * dx * h_outside / k_mud)
            * (outside_temperature - T_wall_mud[0])
        )
    )

    # Interior boundary
    T_wall_mud_new[-1] = (
        T_wall_mud[-1]
        + alpha_mud * dt / dx**2
        * (
            2 * T_wall_mud[-2]
            - 2 * T_wall_mud[-1]
            - (2 * dx * h_inside / k_mud)
            * (T_wall_mud[-1] - T_room_mud)
        )
    )

    # Room air energy balance
    heat_flux_mud = h_inside * (
        T_wall_mud[-1] - T_room_mud
    )

    T_room_mud += (
        heat_flux_mud
        * wall_area
        * dt
        / (room_air_mass * cp_air)
    )

    T_wall_mud[:] = T_wall_mud_new


    # --------------------------------------------------------
    # CONCRETE MODEL
    # --------------------------------------------------------

    conduction_concrete = (
        alpha_concrete
        * dt
        / dx**2
        * (
            T_wall_concrete[2:]
            - 2 * T_wall_concrete[1:-1]
            + T_wall_concrete[:-2]
        )
    )

    T_wall_concrete_new[1:-1] = (
        T_wall_concrete[1:-1] + conduction_concrete
    )

    # Exterior boundary
    T_wall_concrete_new[0] = (
        T_wall_concrete[0]
        + alpha_concrete * dt / dx**2
        * (
            2 * T_wall_concrete[1]
            - 2 * T_wall_concrete[0]
            + (2 * dx * h_outside / k_concrete)
            * (outside_temperature - T_wall_concrete[0])
        )
    )

    # Interior boundary
    T_wall_concrete_new[-1] = (
        T_wall_concrete[-1]
        + alpha_concrete * dt / dx**2
        * (
            2 * T_wall_concrete[-2]
            - 2 * T_wall_concrete[-1]
            - (2 * dx * h_inside / k_concrete)
            * (T_wall_concrete[-1] - T_room_concrete)
        )
    )

    # Room air energy balance
    heat_flux_concrete = h_inside * (
        T_wall_concrete[-1] - T_room_concrete
    )

    T_room_concrete += (
        heat_flux_concrete
        * wall_area
        * dt
        / (room_air_mass * cp_air)
    )

    T_wall_concrete[:] = T_wall_concrete_new


    # --------------------------------------------------------
    # STORE RESULTS
    # --------------------------------------------------------

    time_history[step] = current_time / 3600.0
    outside_temperature_history[step] = outside_temperature
    inside_mud_history[step] = T_room_mud
    inside_concrete_history[step] = T_room_concrete


print("Simulation complete.")


# ============================================================
# 8. VISUALISATION
# ============================================================

plt.figure(figsize=(12, 7))

plt.plot(
    time_history,
    outside_temperature_history,
    label="Outdoor temperature",
    linestyle="--",
    alpha=0.5
)

plt.plot(
    time_history,
    inside_mud_history,
    label="Mud / Bhunga room",
    linewidth=2
)

plt.plot(
    time_history,
    inside_concrete_history,
    label="Concrete room",
    linewidth=2
)

plt.xlabel("Time (hours)")
plt.ylabel("Temperature (°C)")
plt.title("Transient Thermal Comparison: Mud vs. Concrete")

plt.grid(True, alpha=0.3)
plt.legend()
plt.xlim(0, total_time / 3600)

plt.tight_layout()
plt.show()
