from flask import current_app, request
from lidarts.openvidu import bp

import requests

@bp.route("/api/sessions", methods=['POST'])
def initializeSession():
    try:
        body = request.json if request.data else {}
        response = requests.post(
            current_app.config['OPENVIDU_URL'] + "openvidu/api/sessions",
            verify=False,
            auth=("OPENVIDUAPP", current_app.config['OPENVIDU_SECRET']),
            headers={'Content-type': 'application/json'},
            json=body
        )
        response.raise_for_status()
        return response.json()["sessionId"]
    except requests.exceptions.HTTPError as err:
        if (err.response.status_code == 409):
            # Session already exists in OpenVidu
            return request.json["customSessionId"]
        else:
            return err
        

@bp.route("/api/sessions/<sessionId>/connections", methods=['POST'])
def createConnection(sessionId):
    body = request.json if request.data else {}
    return requests.post(
        current_app.config['OPENVIDU_URL'] + "openvidu/api/sessions/" + sessionId + "/connection",
        verify=False,
        auth=("OPENVIDUAPP", current_app.config['OPENVIDU_SECRET']),
        headers={'Content-type': 'application/json'},
        json=body
    ).json()["token"]