To configure vnc and x server, you need to follow this instruction.

1)

```sudo apt update```

```sudo apt install xfce4 xfce4-goodies tightvncserver```

2) 

```vncserver```

(Enter password)

3) 

```vncserver -kill :1```

4)

```nano ~/.vnc/xstartup```

Remove all and paste this:

```
#!/bin/bash
xrdb $HOME/.Xresources
startxfce4 &
```

5)
```vncserver```
 

Than you can connect with any VNC client like [Real VNC](https://www.realvnc.com/en/connect/download/viewer/) to 
your server. 

(Note that the port depends on your screen number, It will be 5900 + screen number. For example for the :1 
screen port will be 5901)
