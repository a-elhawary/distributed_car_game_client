import zmq
from threading import Thread 
import pickle
import requests
import json


class ClientMiddleware:
    # Client info
    game_id = None
    player_id = None 

    # auth server address
    AUTH_SERVER = "http://178.79.139.125:5000"

    # server addresses
    TRACKERS = [] 
    SUBSCRIBE_PORT = "7878"
    PUSH_PORT = "8787"
    REQ_PORT = "12345"

    # my ports
    sub_sock = None
    push_sock = None
    req_sock = None

    # state data
    current_state = {}
    state_modified = False
    start_game = False

    # recieved chat buffer
    recv_msgs = []

    # Make Singleton
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(ClientMiddleware, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        context = zmq.Context()
        self.sub_sock = context.socket(zmq.SUB)
        self.push_sock = context.socket(zmq.PUSH)
        self.req_sock = context.socket(zmq.REQ)

    # Auth Server Functions
    def login(self, user_name, password):
        res = requests.post(self.AUTH_SERVER + "/login", data={"user_name" : user_name, "password": password})
        return res.text

    def register(self, user_name, password):
        res = requests.post(self.AUTH_SERVER + "/register", data={"user_name" : user_name, "password": password})
        return res.text

    def list_games(self):
        res = requests.get(self.AUTH_SERVER + "/list_games")
        return json.loads(res.text)

    def create_game(self, game_name, num_players):
        res = requests.post(self.AUTH_SERVER + "/create_game", data={"game_name":game_name, "num_players": num_players})
        return json.loads(res.text)
        

    # Tracker Functions
    def start(self):
        t1 = Thread(target=self.getStateUpdate)
        t1.start()
    
    def getNewState(self):
        self.req_sock.connect("tcp://"+self.SERVER_IP[0]+":"+self.REQ_PORT)
        msg = str(self.game_id) + " GS"
        self.req_sock.send(msg.encode())
        self.current_state = pickle.loads(self.req_sock.recv())
        self.state_modified = True
        self.req_sock.close()
    
    def move(self, direction):
        self.push_sock.send_string(str(self.game_id) + " " + self.player_id + " G " + direction)
    
    def sendChatMessage(self, msg):
        self.push_sock.send_string(str(self.game_id) + " " + self.player_id + " C " + msg)
    
    def getStateUpdate(self):
        while True:
            data = self.sub_sock.recv().decode().split()
            game_id = data[0]
            player_id = data[1]
            if(len(data) > 2):
                msg_type = data[2]
                data = data[3:]
            if player_id == "START":
                self.current_state["Status"] = "Ongoing"
                self.start_game = True
                self.state_modified = True
                continue
            elif player_id == "STOP":
                self.current_state["Status"] = "Done"
                self.state_modified = True
            if msg_type == "C":
                myStr = ""
                for word in data:
                    myStr += word
                    myStr += " "
                myStr = myStr[:len(myStr)-1]
                self.recv_msgs.append((player_id, myStr))
            elif msg_type == "G":
                for player in self.current_state["Players_Info"]:
                    if player["ID"] == player_id:
                        player["Position_X"] = int(data[0])
                        player["Position_Y"] = int(data[1])
                        self.state_modified = True
            elif msg_type == "R":
                for player in self.current_state["Players_Info"]:
                    if player["ID"] == player_id:
                        player["Ready"] = 1 
                        self.state_modified = True
            elif msg_type == "J":
                self.current_state["Players_Info"].append({"ID": player_id, "Position_X": data[0], "Position_Y": data[1], "Ready": 0})
                self.state_modified = True

    # Setters and Getters
    def setUserID(self, player_id):
        self.player_id = player_id

    def joinGame(self, game_id, trackers):
        # subscirbe and join
        for tracker in trackers:
            self.sub_sock.connect("tcp://"+tracker+":"+self.SUBSCRIBE_PORT)
            self.push_sock.connect("tcp://"+tracker+":"+self.PUSH_PORT)
        self.sub_sock.setsockopt(zmq.SUBSCRIBE, str(game_id).encode())

        # start listening
        self.start()

        # setting up some state
        self.game_id = game_id
        self.SERVER_IP = trackers

        # getting current game state
        self.getNewState()
        if self.current_state["Status"] != "Starting":
            self.start_game = True

        # if user is not in state then send join message
        found = False
        for player in self.current_state["Players_Info"]:
            if player["ID"] == self.player_id:
                found = True
        if not found:
            self.push_sock.send_string("%s %s J" % (self.game_id, self.player_id))

    def makeReady(self):
        self.push_sock.send_string("%s %s R" % (self.game_id, self.player_id))

    def isMine(self, player_id):
        return self.player_id == player_id

    def getMessages(self):
        return self.recv_msgs

    def getOneMessage(self):
        return self.recv_msgs.pop(0)

    def isStateChanged(self):
        return self.state_modified
    
    def isStartGame(self):
        self.state_modified = False
        return self.start_game

    def getState(self):
        self.state_modified = False
        return self.current_state
