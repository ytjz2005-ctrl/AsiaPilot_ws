# AsiaPilot: Deployable Differentiable Physics-Based Agile Flight 🚀

![Ubuntu](https://img.shields.io/badge/Ubuntu-20.04-orange.svg)
![ROS](https://img.shields.io/badge/ROS-Noetic-blue.svg)
![Python](https://img.shields.io/badge/Python-3.11-blue.svg)
![PyTorch](https://img.shields.io/badge/PyTorch-%E2%89%A52.0.0-EE4C2C.svg)

This project is an improved and engineering-oriented implementation based on the **"Differentiable Physics-Based End-to-End Agile Flight Obstacle Avoidance"** framework proposed by the team from Shanghai Jiao Tong University (SJTU).

Although the original project is outstanding in theory and algorithms, it lacks specific approaches and interfaces for direct deployment on real-world UAV flight controllers. Starting from this point, **this project successfully builds a bridge between the obstacle avoidance planner and the low-level flight controller via MAVROS. It provides highly clear control logic and runs successfully in the Gazebo simulation environment.** This project aims to bridge the "last mile" from cutting-edge algorithms to real-world UAV deployment.

## ✨ Highlights

- 🌉 **Flight Controller Bridge**: This is the core contribution of this project. Through MAVROS nodes, we successfully connected the neural network-based end-to-end planner with the PX4 flight controller, providing verified control logic and communication interfaces for real-world deployment.
- 🚁 **Complete Simulation Loop**: Achieved a complete closed-loop pipeline from "Vision/State Input -> Neural Network Planner -> MAVROS Command Dispatch -> PX4 Low-level Response -> Gazebo Physics Simulation".
- 📦 **Out-of-the-Box**: All third-party large files and pre-trained weights are directly included in the repository. **No extra download links are needed.** Just clone and you are ready to go.

## 🛠 Requirements

- **OS**: Ubuntu 20.04
- **ROS**: Noetic
- **Python**: 3.11
- **Deep Learning**: PyTorch 2.0.0 or higher

---

## ⚙️ Installation & Setup

Please strictly follow the steps below to set up your environment.

### 1. Prepare Workspace & Install Gazebo / MAVROS
```bash
# Enter the workspace
cd ~/AsiaPilot_ws

# Grant execution permissions to install scripts
chmod +x scripts/install_*.sh

# Install Gazebo
bash scripts/install_gazebo.sh

# Install MAVROS
bash scripts/install_mavros.sh
```

### 2. Install and Build PX4 (v1.13.3)
```bash
# Clone PX4 with the specific version
git clone https://github.com/PX4/PX4-Autopilot.git --recursive --branch v1.13.3
cd ~/PX4-Autopilot

# Update submodules
git submodule update --init --recursive

# Run Ubuntu environment setup script
source ./Tools/setup/ubuntu.sh

# Clean and build the SITL simulation environment
rm -rf ~/PX4-Autopilot/build
make px4_sitl_default gazebo-classic_iris
```

### 3. Configure Environment Variables
Open your `~/.bashrc` file:
```bash
vim ~/.bashrc
```
Add the following lines to the **end** of the file to configure PX4 and ROS environment paths:
```bash
source ~/PX4-Autopilot/Tools/setup_gazebo.bash ~/PX4-Autopilot/ ~/PX4-Autopilot/build/px4_sitl_default
export ROS_PACKAGE_PATH=$ROS_PACKAGE_PATH:~/PX4-Autopilot
export ROS_PACKAGE_PATH=$ROS_PACKAGE_PATH:~/PX4-Autopilot/Tools/sitl_gazebo
```
After saving and exiting, source the environment variables:
```bash
source ~/.bashrc
```

### 4. Install Python Dependencies
```bash
sudo apt install python3-pip
pip3 install --user toml empy jinja2 packaging
# Make sure you have installed PyTorch satisfying the requirements (>= 2.0.0)
```

### 5. Build the Workspace
```bash
cd ~/AsiaPilot_ws
catkin_make
```

---

## 🚀 Running the Simulation

After completing all the configurations and building successfully, you can launch the end-to-end agile flight obstacle avoidance simulation:

```bash
# Enter workspace and source environment
cd ~/AsiaPilot_ws
source ~/.bashrc
source devel/setup.bash

# Launch the simulation
roslaunch easondrone_gazebo simulation.launch
```

---

## 🧠 Model Training
The pre-trained model weights included in this repository are ready for direct inference. If you wish to train your own models, please refer to the official training framework:

👉 [DiffPhysDrone - Training Framework](https://github.com/HenryHuYu/DiffPhysDrone)

---

## 👨‍💻 Author

- **Janzhe Yutao**

---

## 📚 References

This project is mainly based on the following outstanding research. If you use this project in your research, please consider citing the following papers:

```bibtex
@article{zhang2025learning,
  title={Learning vision-based agile flight via differentiable physics},
  author={Zhang, Yuang and Hu, Yu and Song, Yunlong and Zou, Danping and Lin, Weiyao},
  journal={Nature Machine Intelligence},
  pages={1--13},
  year={2025},
  publisher={Nature Publishing Group}
}

@inproceedings{Loquercio2021Science,
  title={Learning High-Speed Flight in the Wild},
  author={Loquercio, Antonio and Kaufmann, Elia and Ranftl, Ren{\'e} and M{\"u}ller, Matthias and Koltun, Vladlen and Scaramuzza, Davide},
  booktitle={Science Robotics}, 
  year={2021}, 
  month={October}, 
} 
```