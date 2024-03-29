# ml_announcements
Code for diffusion maps, announcements, and macrofinancial variables project

# Prerequisites
[Docker](https://docs.docker.com/get-started)

# Setup 
The docker image takes care of all the dependencies needed to run the code; thus, no need to install additional libraries. 
The image only needs to be built once. However, you need to run the image each time. In the root directory, run:
<ol>
<li> Build docker image: 

```
docker build -t mla-image:latest ./dockerfiles
```
Notice that you might need Admin access
<li> Run image at port 5000:

```
docker run -it -p 5000:5000 -v <path_to_source>:/root mla-image
```
Use a different port if 5000 is busy for you. Replace <path_to_source> to your path to the source of the project. Do not include the < > symbols. 

</ol>


# Jupyter

Running jupyter inside a docker container is almost the same as before. Run:
```
jupyter notebook --port=5000 --no-browser --ip=0.0.0.0 --allow-root
```
Then navigate to: ```http://localhost:5000```. The browser may ask you for a token, the token was printed in the terminal after running the previous command.

Navigate to the notebook you want. For example, the notebook for the FFN is in models/ffn.ipynb, and the notebook for the difussion maps is in models/difussion_map.ipynb

# Comments
You need to use the same port everywhere. That is, if you are running the docker container in a different port, the jupyter notebook should run in the same port. 
