import gamelib
import random
import math
import warnings
from sys import maxsize

"""
Most of the algo code you write will be in this file unless you create new
modules yourself. Start by modifying the 'on_turn' function.

Advanced strategy tips: 

Additional functions are made available by importing the AdvancedGameState 
class from gamelib/advanced.py as a replcement for the regular GameState class 
in game.py.

You can analyze action frames by modifying algocore.py.

The GameState.map object can be manually manipulated to create hypothetical 
board states. Though, we recommended making a copy of the map to preserve 
the actual current map state.
"""

class AlgoStrategy(gamelib.AlgoCore):
    def __init__(self):
        super().__init__()
        random.seed()

    def on_game_start(self, config):
        """ 
        Read in config and perform any initial setup here 
        """
        gamelib.debug_write('Configuring your custom algo strategy...')
        self.config = config
        global FILTER, ENCRYPTOR, DESTRUCTOR, PING, EMP, SCRAMBLER
        FILTER = config["unitInformation"][0]["shorthand"]
        ENCRYPTOR = config["unitInformation"][1]["shorthand"]
        DESTRUCTOR = config["unitInformation"][2]["shorthand"]
        PING = config["unitInformation"][3]["shorthand"]
        EMP = config["unitInformation"][4]["shorthand"]
        SCRAMBLER = config["unitInformation"][5]["shorthand"]

    # returns a list of firewall infos
    # a firewall info contains {unit-type, x, y, possibility}
    # possibility = the possibility we predict enemy will spawn
    #               a specified unit type at specified x-y coordinate next turn
    #               this will be useful when calculating scores
    def predict_enemy_firewalls(self, game_state):
        return []

    # returns a list of firewall infos (see above) with possibility = 1
    def get_player_firewalls(self, game_state):
        return []

    # predict enemy state at the start of next turn, 
    def pred_enemy_state(self, game_state):
        health=30
        # get list of firewalls of player passed in
        listFirewalls=self.predict_enemy_firewalls(game_state)
        bits=game_state.get_resource(game_state.BITS, 1)
        cores=game_state.get_resource(game_state.CORES, 1)
        return [health, listFirewalls, bits, cores]
    
    # get details of a player's stat (health, existing stationary units, resources)
    def get_player_state(self, game_state):
        health=30
        # get list of firewalls of player passed in
        listFirewalls=self.get_player_firewalls(game_state)
        bits=game_state.get_resource(game_state.BITS)
        cores=game_state.get_resource(game_state.CORES)
        return [health, listFirewalls, bits, cores]

    def generate_strategies(self, player_state, enemy_state):
        # return value: list of {unit_type, x, y} : 
        # each item in the list is instruction on where to deploy specific units
        return []

    # this function evaluates the effectiveness of a strategy
    # based on current player state and expected enemy state
    # returns a number
    def evaluate(self, strat, player_state, enemy_state):
        # general idea here: score = est_player_score - est_enemy_score
        # est_player_score = k_1 * health + k_2 * (resources after executing strat) + 
        #                    k_3 * (calculated firewall scores after strat)
        # est_player_score = k_1 * health + k_2 * (enemy resources) + 
        #                    k_3 * (calculated enemy firewall scores)
        return 0

    # strat: list of deploy instructions, 
    # each instruction should contain {unit_type, x, y}
    def execute_strat(self, strat):
        pass

    def findEnc(self):
        return "left"

    def on_turn(self, turn_state):
        """
        This function is called every turn with the game state wrapper as
        an argument. The wrapper stores the state of the arena and has methods
        for querying its state, allocating your current resources as planned
        unit deployments, and transmitting your intended deployments to the
        game engine.
        """

        game_state = gamelib.GameState(self.config, turn_state)
        gamelib.debug_write('Performing turn {} of your custom algo strategy'.format(game_state.turn_number))
        #game_state.suppress_warnings(True)  #Uncomment this line to suppress warnings.
        player_state = self.get_player_state(game_state)
        enemy_state = self.pred_enemy_state(game_state)

        strats = self.generate_strategies(player_state, enemy_state)
        if(len(strats) != 0):
            best_strat = strats[0]
            best_score = self.evaluate(best_strat, player_state, enemy_state)
            for strat in strats[1:]:
                score = self.evaluate(best_strat, player_state, enemy_state)
                if(score > best_score):
                    best_score = score
                    best_strat = strat

        self.execute_strat(best_strat)
        game_state.submit_turn()


############################################################################################

    """
    NOTE: Below are helper functions that might be useful later-on
    All the methods after this point are part of the sample starter-algo
    strategy and can safey be replaced for your custom algo.
    """
    def starter_strategy(self, game_state):
        """
        Build the C1 logo. Calling this method first prioritises
        resources to build and repair the logo before spending them 
        on anything else.
        """
        self.build_c1_logo(game_state)

        """
        Then build additional defenses.
        """
        self.build_defences(game_state)

        """
        Finally deploy our information units to attack.
        """
        self.deploy_attackers(game_state)

    # Here we make the C1 Logo!
    def build_c1_logo(self, game_state):
        """
        We use Filter firewalls because they are cheap

        First, we build the letter C.
        """
        firewall_locations = [[8, 11], [9, 11], [7,10], [7, 9], [7, 8], [8, 7], [9, 7]]
        for location in firewall_locations:
            if game_state.can_spawn(FILTER, location):
                game_state.attempt_spawn(FILTER, location)
        
        """
        Build the number 1.
        """
        firewall_locations = [[17, 11], [18, 11], [18, 10], [18, 9], [18, 8], [17, 7], [18, 7], [19,7]]
        for location in firewall_locations:
            if game_state.can_spawn(FILTER, location):
                game_state.attempt_spawn(FILTER, location)

        """
        Build 3 dots with destructors so it looks neat.
        """
        firewall_locations = [[11, 7], [13, 9], [15, 11]]
        for location in firewall_locations:
            if game_state.can_spawn(DESTRUCTOR, location):
                game_state.attempt_spawn(DESTRUCTOR, location)

    def build_defences(self, game_state):
        """
        First lets protect ourselves a little with destructors:
        """
        destructor_locations = [[3, 12], [6, 12], [11, 12], [16, 12], [21, 12], [24, 12]]
        # Will eliminate all the coordinates that is already placed
        destructor_locations = self.filter_blocked_locations(destructor_locations, game_state)
        for location in destructor_locations:
            if game_state.can_spawn(DESTRUCTOR, location):
                game_state.attempt_spawn(DESTRUCTOR, location)

        """
        Then build filters at the top of the arena that
        destructors do not cover
        """
        filter_locations = [[3, 13], [6, 13], [11, 13], [16, 13], [21, 13], [24, 13]]
        filter_locations = self.filter_blocked_locations(filter_locations, game_state)
        for location in filter_locations:
            if game_state.can_spawn(FILTER, location):
                game_state.attempt_spawn(FILTER, location)

        # Depending on where the enemy encryptor is, create 3 more walls.
        if (self.findEnc() == 'left'):
            filter_locations = [[0, 13], [1, 13], [2, 13]]
        elif (self.findEnc() == 'right'):
            filter_locations = [[25, 13], [26, 13], [27, 13]]
        else:
            filter_locations = []
        for location in filter_locations:
            if game_state.can_spawn(FILTER, location):
                game_state.attempt_spawn(FILTER, location)

        """
        Then lets boost our offense by building some encryptors to shield 
        our information units. Lets put them near the front because the 
        shields decay over time, so shields closer to the action 
        are more effective.
        """
        # For now, do not worry about encryptors
        # encryptor_locations = [[19, 10], [7, 10]]
        # for location in encryptor_locations:
        #     if game_state.can_spawn(ENCRYPTOR, location):
        #         game_state.attempt_spawn(ENCRYPTOR, location)

        """
        Lastly lets build encryptors in random locations. Normally building 
        randomly is a bad idea but we'll leave it to you to figure out better 
        strategies. 

        First we get all locations on the bottom half of the map
        that are in the arena bounds.
        """
        # all_locations = []
        # for i in range(game_state.ARENA_SIZE):
        #     for j in range(math.floor(game_state.ARENA_SIZE / 2)):
        #         if (game_state.game_map.in_arena_bounds([i, j])):
        #             all_locations.append([i, j])
        
        """
        Decide where to put additional destructors
        """
        if (self.findEnc() == 'left'):
            possible_locations = [[23, 12], [20, 12]]
        elif (self.findEnc() == 'right'):
            possible_locations = [[4, 12], [7, 12]]

        """
        While we have cores to spend, build additional destructor.
        """
        for location in possible_locations:
            if game_state.get_resource(game_state.CORES) >= 15:
                game_state.attempt_spawn(DESTRUCTOR, location)

        # If we have enough cores, build encryptors
        encryptor_locations = [[5, 11], [6, 11], [7, 11]]
        for location in encryptor_locations:
            if game_state.get_resource(game_state.CORES) >= 15:
                game_state.attempt_spawn(ENCRYPTOR, location)


    def deploy_attackers(self, game_state):
        """
        First lets check if we have 10 bits, if we don't we lets wait for 
        a turn where we do.
        """
        if (game_state.get_resource(game_state.BITS) < 10):
            return
        
        """
        First lets deploy an EMP long range unit to destroy firewalls for us.
        """
        if game_state.can_spawn(EMP, [3, 10]):
            game_state.attempt_spawn(EMP, [3, 10])

        """
        Now lets send out 3 Pings to hopefully score, we can spawn multiple 
        information units in the same location.
        """
        if game_state.can_spawn(PING, [14, 0], 3):
            game_state.attempt_spawn(PING, [14,0], 3)

        """
        NOTE: the locations we used above to spawn information units may become 
        blocked by our own firewalls. We'll leave it to you to fix that issue 
        yourselves.

        Lastly lets send out Scramblers to help destroy enemy information units.
        A complex algo would predict where the enemy is going to send units and 
        develop its strategy around that. But this algo is simple so lets just 
        send out scramblers in random locations and hope for the best.

        Firstly information units can only deploy on our edges. So lets get a 
        list of those locations.
        """
        friendly_edges = game_state.game_map.get_edge_locations(game_state.game_map.BOTTOM_LEFT) + game_state.game_map.get_edge_locations(game_state.game_map.BOTTOM_RIGHT)
        
        """
        Remove locations that are blocked by our own firewalls since we can't 
        deploy units there.
        """
        deploy_locations = self.filter_blocked_locations(friendly_edges, game_state)
        
        """
        While we have remaining bits to spend lets send out scramblers randomly.
        """
        while game_state.get_resource(game_state.BITS) >= game_state.type_cost(SCRAMBLER) and len(deploy_locations) > 0:
           
            """
            Choose a random deploy location.
            """
            deploy_index = random.randint(0, len(deploy_locations) - 1)
            deploy_location = deploy_locations[deploy_index]
            
            game_state.attempt_spawn(SCRAMBLER, deploy_location)
            """
            We don't have to remove the location since multiple information 
            units can occupy the same space.
            """
        
    def filter_blocked_locations(self, locations, game_state):
        filtered = []
        for location in locations:
            if not game_state.contains_stationary_unit(location):
                filtered.append(location)
        return filtered

if __name__ == "__main__":
    algo = AlgoStrategy()
    algo.start()
