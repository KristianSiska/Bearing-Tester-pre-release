import numpy as np
ALL_BEARING_TORQUE = 0.000125
TOTAL_ROTATIONAL_MOMENT = 0.00000572
AERODYNAMIC_FRICTION_FORCE_RADIUS = 0.0175
WIDTH_OF_FLYWHEEL = 0.029
AERODYNAMIC_FRICTION_DRAG_AREA = 0.003830125
AERODYNAMIC_FRICTION_DRAG_COEFICIENT = 0.00250
AIR_DENSITY = 1.23

def predict_speed(starting_val, steps, interval):
    # Constants
    

    # Convert starting value to angular velocity in rad/s
    starting_angular_velocity = starting_val * 2 * np.pi
    
    # Initialize angular velocity
    angular_velocity = starting_angular_velocity
    
    rps_list = []
    rps = starting_angular_velocity / (2 * np.pi)
    rps_list.append(rps)

    # Loop through steps to predict speed
    for i in range(steps):
        # Calculate tangential speed
        tangential_speed = AERODYNAMIC_FRICTION_FORCE_RADIUS * angular_velocity
        
        # Calculate aerodynamic drag torque
        aero_drag_torque = 0.5 * AIR_DENSITY * AERODYNAMIC_FRICTION_DRAG_COEFICIENT * AERODYNAMIC_FRICTION_DRAG_AREA * tangential_speed**2

        # Calculate total torque
        total_torque = aero_drag_torque + ALL_BEARING_TORQUE

        # Calculate angular acceleration
        angular_acceleration = total_torque / TOTAL_ROTATIONAL_MOMENT

        # Update angular velocity using Euler's method
        angular_velocity -= interval * angular_acceleration
        
        # Convert angular velocity to revolutions per second (RPS)
        rps = angular_velocity / (2 * np.pi)
        rps_list.append(rps)

    return rps_list

# Parameters
starting_value = 150
time_steps = 20
time_interval = 1.0193  # seconds
if __name__ == "__main__":
    # Predict speed
    rps_list = predict_speed(starting_value, time_steps, time_interval)

    # Print the final angular velocity
    #print("Final Angular Velocity (RPS):", rps_list[-1])
    for i in range(len(rps_list)):
        print(f"index {i}:  {rps_list[i]}")