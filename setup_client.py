import sys
from cx_Freeze import setup, Executable


build_exe_options = {
            "packages" :
                [ "os", "sys", "rsa", "cryptography", "logging", "queue", "ssl", "socket", "hmac"  ],
            "excludes" :
                [""],
            "zip_include_packages":
                [""],
            }


setup(
name= "myscript" ,
version= "1.0" ,
description= "My messenger client" ,
options={
"build_exe" : build_exe_options
},
executables=[Executable( "client/src/graphic_chat.py" , targetName='client.exe', base='Win32GUI')]
)