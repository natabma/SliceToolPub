# SliceTool - A tool for slicing 3D-Objects

## About
Slice Tool is a utility for easy and quick creation of many equidistant slices of the surface of a 3D object. It was made to assist textile researchers working with 3D scans of human bodyparts, e.g. when designing compression socks.

## Usage
The usage is demonstrated in a a quick video.

## Features
| Scaling | Trimming |
| <img src="./img/scaling.png" width="500"> | <img src="./img/trimming.png" width="500"> |
| Slicing | Results |
| <img src="./img/slicing.png" width="500"> | <img src="./img/results.png" width="500">  |

## Installation
First, download this repository and unpack it. Notice that the folder must be on your local harddrive.

### Prebuilt Executable
Windows Users who just want to use the tool in its current state may use the pre built executable located in "dist". 

### Run from Source

1) Create a virtual environment in the folder. Python 11.9 is recommended.
2) Install the requirements by calling 'pip install -r requirements. txt'.
3) **IMPORTANT:** SliceTool uses the vedo library (https://github.com/marcomusy/vedo). Certain bugfixes of that package which are necessary for SliceTool to properly function are not included in its currently most recent version (2025.5.4) on PyPi. Instead, please download the vedo package directly from its repository and replace the vedo folder in your repository by it. 
   


   