from flask import Flask, request
import subprocess


app=Flask(__name__)


@app.route("/aibix", methods=["POST"])
def hook():
    print(request.data)
    result = subprocess.run(["ansible-playbook", "vyos-setup.yml", "-l", "p3r8v"], capture_output=True, text=True)
    #sresult = subprocess.run(["ls", "-l"], capture_output=True, text=True, shell=True)
    if result.returncode == 0:
        return "alles super:" + result.stdout
    else:
        return "kaputt: " + result.stderr


if __name__ == "__main__":
    app.run(host='0.0.0.0')
