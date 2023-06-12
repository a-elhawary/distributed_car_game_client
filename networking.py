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
    SERVER_IP = "127.0.0.1"
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
        self.sub_sock.connect("tcp://"+self.SERVER_IP+":"+self.SUBSCRIBE_PORT)
        self.push_sock = context.socket(zmq.PUSH)
        self.push_sock.connect("tcp://"+self.SERVER_IP+":"+self.PUSH_PORT)
        self.req_sock = context.socket(zmq.REQ)
        self.sub_sock.setsockopt(zmq.SUBSCRIBE, str(self.game_id).encode())

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
        return res
        

    # Tracker Functions
    
    def start(self):
        print("starting server...")
        t1 = Thread(target=self.getStateUpdate)
        t2 = Thread(target=self.getNewState)
        t1.start()
        t2.start()
    
    def getNewState(self):
        self.req_sock.connect("tcp://"+self.SERVER_IP+":"+self.REQ_PORT)
        msg = str(self.game_id) + " GS"
        self.req_sock.send(msg.encode())
        self.current_state = pickle.loads(self.req_sock.recv())
        print("initialized")
        print(self.current_state)
        state_modified = True
        self.req_sock.close()
    
    def move(self, direction):
        self.push_sock.send_string(str(self.game_id) + " " + self.player_id + " G " + direction)
    
    def sendChatMessage(self, msg):
        self.push_sock.send_string(str(self.game_id) + " " + self.player_id + " C " + msg)
    
    def getStateUpdate(self):
        print("listening for subscribe socket")
        while True:
            data = self.sub_sock.recv().decode().split()
            game_id = data[0]
            player_id = data[1]
            msg_type = data[2]
            data = data[3:]
            print('recieved something')
            if msg_type == "C":
                myStr = ""
                for word in data:
                    myStr += word
                    myStr += " "
                myStr = myStr[:len(myStr)-1]
                print("Chat sent by " + player_id)
                print(myStr)
                self.recv_msgs.append((player_id, myStr))
            elif msg_type == "G":
                for player in self.current_state["Players_Info"]:
                    if player["ID"] == player_id:
                        player["Position_X"] = int(data[0])
                        player["Position_Y"] = int(data[1])
                        print("new position")
                        print(self.current_state)
                        self.state_modified = True

    # Setters and Getters
    def setUserID(self, player_id):
        self.player_id = player_id

    def setGameID(self, game_id):
        self.game_id = game_id

    def isMine(self, player_id):
        return self.player_id == player_id

    def getMessages(self):
        return self.recv_msgs

    def getOneMessage(self):
        return self.recv_msgs.pop(0)

    def isStateChanged(self):
        return self.state_modified

    def getState(self):
        self.state_modified = False
        return self.current_state
