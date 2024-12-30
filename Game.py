import tkinter as tk
import time
import math
import datetime

from Base import *
from Towers import *
from Colors import *
from Waves import *
from Maps import *
from ScreenConvert import *
from _datetime import date, datetime

logf = open("Log.log", "a+")

class GameTop():
    logf = open("Log.log", "a+")
    background = ()
    background_image = ()
    
    def __init__(self):
        self.alive = True
        self.godmode = False
        
        # Instantiate tk window and set up frames
        self.root = tk.Tk()
        self.root.geometry("%dx%d%+d%+d" % (screenWidth, screenHeight, 100, 50))
        self.root.protocol('WM_DELETE_WINDOW', self.delete)

        self.game_frame = tk.Frame(self.root, width=(screenWidth * widthMultiplier), height=(screenHeight * .9))  # creates embed frame for pg window
        self.game_frame.grid(row=0, column=0, rowspan=3)

        self.menu_frame = tk.Frame(self.root, width=screenWidth * (1 - widthMultiplier), height=(screenHeight * heightMultiplier))
        self.menu_frame.grid(row=0, column=1)

        info_frame = tk.Frame(self.menu_frame)
        info_frame.place(anchor="n", relx=0.5, rely=0)

        # Money and Health variables
        self.money = 40
        self.health = 100
        
        if self.godmode:
            self.money = 500000
            self.health = 10

        # Money and Health labels
        self.money_label = tk.Label(info_frame, text="$: " + str(self.money), font=("Candara", 20))
        self.health_label = tk.Label(info_frame, text="<3: " + str(self.health), font=("Candara", 20))
        self.money_label.grid(row=0)
        self.health_label.grid(row=1)

        # Wave count and play button
        self.wave = 1
        self.wave_button = tk.Button(info_frame, text="wave 1\nstart", font=("Candara", 15), width=6, height=2,
                                     command=self.play_wave)
        self.wave_button.grid(row=2, column=0)

        # Tower Buttons
        button_frame = tk.Frame(self.menu_frame)
        button_frame.place(anchor="n", relx=0.5, rely=0.2)

        # Tower buttons scroll bar and canvas
        vscrollbar = tk.Scrollbar(button_frame)
        vscrollbar.grid(row=0, column=1, sticky="ns")

        button_canvas = tk.Canvas(button_frame, yscrollcommand=vscrollbar.set, width=160, height=360)
        button_canvas.grid(row=0, column=0)

        vscrollbar.config(command=button_canvas.yview)

        # Actual tower buttons
        inner_button_frame = tk.Frame(button_canvas)

        self.tower_buttons = [
            tk.Button(inner_button_frame, text=Archer.name + "\n$" + str(Archer.cost), font=("Candara", 20),
                      width=10, height=2, command=lambda: self.place_tower(0)),
            tk.Button(inner_button_frame, text=Mage.name + "\n$" + str(Mage.cost), font=("Candara", 20),
                      width=10, height=2, command=lambda: self.place_tower(1)),
            tk.Button(inner_button_frame, text=Artillery.name + "\n$" + str(Artillery.cost), font=("Candara", 20),
                      width=10, height=2, command=lambda: self.place_tower(2)),
            tk.Button(inner_button_frame, text=Sniper.name + "\n$" + str(Sniper.cost), font=("Candara", 20),
                      width=10, height=2, command=lambda: self.place_tower(3)),
            tk.Button(inner_button_frame, text=Wall.name + "\n$" + str(Wall.cost), font=("Candara", 20),
                      width=10, height=2, command=lambda: self.place_tower(4))
        ]
        for i in range(len(self.tower_buttons)):
            self.tower_buttons[i].grid(row=i, column=0)

        button_canvas.create_window(0, 0, anchor="nw", window=inner_button_frame)
        inner_button_frame.update_idletasks()
        button_canvas.config(scrollregion=button_canvas.bbox("all"))

        # Instantiate Upgrade Frame
        self.upgrade_frame = tk.LabelFrame(self.menu_frame, text="", font=("Candara", 15))
        self.upgrade_labels = [
            tk.Label(self.upgrade_frame, text="Health:", font=("Candara", 13)),
            tk.Label(self.upgrade_frame, text="Damage:", font=("Candara", 13)),
            tk.Label(self.upgrade_frame, text="Speed:", font=("Candara", 13)),
            tk.Label(self.upgrade_frame, text="Range:", font=("Candara", 13)),
            tk.Label(self.upgrade_frame, text="Regen:", font=("Candara", 13))
        ]
        self.upgrade_amounts = [
            tk.Label(self.upgrade_frame, text="", font=("Candara", 13)),
            tk.Label(self.upgrade_frame, text="", font=("Candara", 13)),
            tk.Label(self.upgrade_frame, text="", font=("Candara", 13)),
            tk.Label(self.upgrade_frame, text="", font=("Candara", 13)),
            tk.Label(self.upgrade_frame, text="", font=("Candara", 13))
        ]
        self.upgrade_buttons = [
            tk.Button(self.upgrade_frame, text="$0", font=("Candara", 13),
                      command=lambda: self.upgrade_selected("health")),
            tk.Button(self.upgrade_frame, text="$0", font=("Candara", 13),
                      command=lambda: self.upgrade_selected("damage")),
            tk.Button(self.upgrade_frame, text="$0", font=("Candara", 13),
                      command=lambda: self.upgrade_selected("speed")),
            tk.Button(self.upgrade_frame, text="$0", font=("Candara", 13),
                      command=lambda: self.upgrade_selected("range")),
            tk.Button(self.upgrade_frame, text="$0", font=("Candara", 13),
                      command=lambda: self.upgrade_selected("regen"))
        ]
        modes = ["first", "last", "closest", "strongest"]
        self.aim_mode = tk.StringVar()
        self.aim_mode_buttons = [tk.Radiobutton(self.upgrade_frame, text=mode, variable=self.aim_mode, value=mode,
                                 command=self.update_mode_selected, font=("Candara", 10)) for mode in modes]
        self.kills_label = tk.Label(self.upgrade_frame, text="", font=("Candara", 10))

        # Instantiate game variables
        self.map = KidMap()
        self.base = Base(self.map.base_position, self.health)
        self.towers = []
        self.enemies = []
        self.projectiles = []
        self.background = background_Image("linearb", (255,255,255), self.map.base_position)
        self.background_image = self.background.getImage()
        # Draw map
        
        # for i in range(len(self.map)-1):
        #    for j in range(self.map.width()-1):
        #        pg.surface.set_at(j,i, (255**(1 / i), (255**(1 / i), (255**(1 / i) ) )))
        points = self.map.map_pixels
        for i in range(len(points) - 1):
            
            start, end = points[i], points[i + 1]
            pg.draw.line(self.background_image, path_color, start, end, 60)
            if i < len(points) - 1:
                pg.draw.circle(self.background_image, path_color, (end[0] + 1, end[1] + 1), 30, 0)

        self.map_mask = pg.mask.from_threshold(self.background_image, path_color, (1, 1, 1, 255))

        # Modify pygame's video output (embeds all new pg windows inside a Tk.Frame object)
        os.environ['SDL_WINDOWID'] = str(self.game_frame.winfo_id())
        os.environ['SDL_VIDEODRIVER'] = 'windib'

        # Instantiate pygame screen
        self.screen = pg.display.set_mode((int(screenWidth * widthMultiplier), int(screenHeight * heightMultiplier)))
        self.update_screen()

        # Update the labels
        self.update_labels()
        
        # Pass the map pixels to the figure out the brown pixels method
        self.map.wrongPixels(self.screen, path_color, self.base)
        # sendSizes(self.root)

    def mainloop(self):
        clock = pg.time.Clock()
        while self.alive:
            clock.tick(60)
            
            if self.health <=0:
                logf.write("I completed the game this time" + datetime + "\n")
                self.alive =False
                


            # Listen for cursor hover over Tower
            mouse_pos = pg.mouse.get_pos()
            for t in self.towers:
                if t.rect.collidepoint(mouse_pos):
                    t.hover = True
                else:
                    t.hover = False

            for event in pg.event.get():
                if event.type == pg.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        for t in self.towers:
                            if t.hover:
                                for t_ in self.towers:
                                    t_.selected = False
                                t.selected = True
                                self.select_tower(t)
                                break
                            else:
                                t.selected = False
                                self.upgrade_frame.place_forget()
                                self.root.update()
                                
            self.update_screen()
            pg.display.update()
            self.root.update()
        
        """Something about the screen updating, printing an you lost message and returning to 'menu' """
        
    def delete(self):
        self.alive = False
        self.root.destroy()

    def get_selected(self):
        for t in self.towers:
            if t.selected:
                return t
        return None

    def update_labels(self):
        self.money_label["text"] = "$: " + str(self.money)
        self.health_label["text"] = "<3: " + str(self.health)

        for i in range(len(tower_types)):
            if self.money < tower_types[i].cost:
                self.tower_buttons[i]["state"] = "disabled"
            else:
                self.tower_buttons[i]["state"] = "normal"

        tower = self.get_selected()

        if tower is None:
            self.upgrade_frame.place_forget()
        else:
            self.upgrade_frame["text"] = tower.name + " Upgrades"
            self.upgrade_amounts[0]["text"] = str(tower.health_level)
            self.upgrade_amounts[1]["text"] = str(tower.damage_level)
            self.upgrade_amounts[2]["text"] = str(tower.speed_level)
            self.upgrade_amounts[3]["text"] = str(tower.range_level)
            self.upgrade_amounts[4]["text"] = str(tower.regen_level)

            self.upgrade_buttons[0]["text"] = "$" + str(tower.get_upgrade_cost("health"))
            self.upgrade_buttons[1]["text"] = "$" + str(tower.get_upgrade_cost("damage"))
            self.upgrade_buttons[2]["text"] = "$" + str(tower.get_upgrade_cost("speed"))
            self.upgrade_buttons[3]["text"] = "$" + str(tower.get_upgrade_cost("range"))
            self.upgrade_buttons[4]["text"] = "$" + str(tower.get_upgrade_cost("regen"))

            for i in range(len(self.upgrade_buttons)):
                if self.money < tower.get_upgrade_cost(["health", "damage", "speed", "range", "regen"][i]) \
                or tower.getLevel(["health", "damage", "speed", "range", "regen"][i]) == 15:
                    self.upgrade_buttons[i]["state"] = "disabled"
                else:
                    self.upgrade_buttons[i]["state"] = "normal"

            for button in self.aim_mode_buttons:
                if button["text"] == tower.aim_mode:
                    button.select()
                else:
                    button.deselect()

            self.kills_label["text"] = "kills: " + str(tower.kills)

        self.root.update()

    def update_screen(self):
        # self.screen.fill(bg_color)        
        self.screen.blit(self.background_image, (0, 0))

        for t in self.towers:
            self.screen.blit(t.image, t.pos)
            pg.draw.rect(self.screen, red, pg.Rect(t.pos.x + 4, t.pos.y - 15, int((t.dims[0] - 6) * (float(t.health) / t.max_health)), 10), 0)
            pg.draw.rect(self.screen, black, pg.Rect(t.pos.x + 2, t.pos.y - 15, t.dims[0] - 4, 10), 2)
            if (t.hover or t.selected )and not isinstance(t, Sniper):
                pg.draw.circle(self.screen, range_color, (int(t.base_center.x), int(t.base_center.y)), t.range, 2)

        for e in self.enemies:
            self.screen.blit(e.image, e.pos)
            pg.draw.rect(self.screen, red, pg.Rect(e.pos.x + 2, e.pos.y - 15, int(48 * (float(e.health) / e.max_health)), 10), 0)
            pg.draw.rect(self.screen, black, pg.Rect(e.pos.x, e.pos.y - 15, 50, 10), 2)

        for p in self.projectiles:
            self.screen.blit(p.image, p.pos)
            
        self.screen.blit(self.base.image, self.base.pos)
        pg.draw.rect(self.screen, red, pg.Rect(self.base.pos.x + 4, self.base.pos.y - 15, int((self.base.dims[0] - 3) * (float(self.base.health) / self.base.max_health)), 10), 0)
        pg.draw.rect(self.screen, black, pg.Rect(self.base.pos.x + 2, self.base.pos.y - 15, self.base.dims[0] - 4, 10), 2)

    def place_tower(self, tower_index):
        for b in self.tower_buttons:
            b["state"] = "disabled"
        self.tower_buttons[tower_index]["relief"] = "ridge"

        TowerType = tower_types[tower_index]
        try:
            preview = TowerType.image.copy()
        except:
            print("no image available")
            self.update_labels()
            self.tower_buttons[tower_index]["relief"] = "raised"
            return
        preview.fill((255, 255, 255, 180), None, pg.BLEND_RGBA_MULT)

        pg.mouse.set_pos(self.screen.get_width() - 10, self.screen.get_height() / 2)  # Initialize mouse at edge
        clock = pg.time.Clock()
        placed = False
        valid_location = True
        while not placed:
            clock.tick(60)

            for event in pg.event.get():
                if event.type == pg.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if valid_location:
                            old = self.get_selected()
                            if old is not None:
                                old.selected = False
                            pos = pg.mouse.get_pos()
                            new = TowerType((pos[0] - TowerType.base_center_pos[0], pos[1] - TowerType.base_center_pos[1]))
                            self.towers.append(new)
                            self.towers.sort(key=lambda t: t.pos.y)  # Sort towers based on y position (for rendering)
                            new.selected = True
                            self.select_tower(new)
                            new.setPosition(pos)

                            self.update_screen()
                            placed = True
                            self.money -= TowerType.cost  # Pay for tower

                    if event.button == 3:
                        placed = True

            self.update_screen()
            pos = pg.mouse.get_pos()

            # Determine if potential tower location is colliding with existing towers, walls, or path
            valid_location = True
            test_rec = pg.Rect(pos[0] - TowerType.base_center_pos[0],
                               pos[1] - TowerType.base_center_pos[1],
                               TowerType.dims[0], TowerType.dims[1])
            test_mask = pg.mask.from_surface(TowerType.image)
            # for t in self.towers:
            #    if test_rec.colliderect(t.rect):
            #        valid_location = False
            #if min(test_rec.topleft) < 0 or test_rec.y + test_rec.height > 900 or test_rec.x + test_rec.width > 1400:  # TODO: fix this!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            #    valid_location = False
            
            # Pass the map pixels to the figure out the brown pixels method
                # wrongPixels(self.screen, path_color)
            
            # for i in badPixels :
                # pos = pg.mouse.get_pos()
            """for pixel in badPixels:
                map_rect_left = min(self.map, key=lambda x: x[0])[0]
                map_rect_top = min(self.map, key=lambda x: x[1])[1]
                p1 = pixel[0]
                p2 = pixel[1]"""
            if pos in  badPixels:
                valid_location = False
            # print(pos)
            
            # print(map_rect_left, map_rect_top)
            # offset = (test_rec.left - map_rect_left, test_rec.top - map_rect_top)
            # print(offset)
            # if self.map_mask.overlap(test_mask, offset) is not None:
            #    valid_location = False

            self.screen.blit(preview, (pos[0] - TowerType.base_center_pos[0], pos[1] - TowerType.base_center_pos[1]))
            if valid_location and not TowerType == Sniper:
                pg.draw.circle(self.screen, black, pos, TowerType.range, 2)
            else:
                if not TowerType == Sniper:
                    pg.draw.circle(self.screen, red, pos, TowerType.range, 2)

            self.root.update()
            pg.display.update()

        self.update_screen()
        pg.display.update()
        self.update_labels()
        self.tower_buttons[tower_index]["relief"] = "raised"


    def upgrade_selected(self, attribute):
        tower = self.get_selected()

        if tower is not None:
            self.money -= tower.get_upgrade_cost(attribute)
            tower.upgrade(attribute)
            self.update_labels()

    def update_mode_selected(self):
        tower = self.get_selected()
        if tower is not None:
            tower.aim_mode = self.aim_mode.get()

    def select_tower(self, tower):
        self.upgrade_frame.place(anchor="n", relx=0.5, rely=0.65)
        self.update_labels()
        for y in range(len(self.upgrade_labels)):
            self.upgrade_labels[y].grid(row=y, column=0)

        for y in range(len(self.upgrade_amounts)):
            self.upgrade_amounts[y].grid(row=y, column=1)

        for y in range(len(self.upgrade_buttons)):
            self.upgrade_buttons[y].grid(row=y, column=2)
        self.root.update()

        for i in range(len(self.aim_mode_buttons)):
            self.aim_mode_buttons[i].grid(row=int(5 + i / 2), column=2 * int(i % 2))

        self.kills_label.grid(row=7, column=1)

    # Called when 'play' is pressed; Runs the next wave
    def play_wave(self):
        
        if len(self.enemies)!= 0 and not self.godmode: #Disables requirement that all enemies off screen before start new wave
            return
        else:
            self.wave_button["text"] = "wave {0}\n...".format(self.wave)
            # self.wave_button["state"] = "disabled"

            # if len(waves) >= self.wave:                 # Generate waves automatically after predefined waves are exhausted
            #     self.enemies = waves[self.wave - 1]
            # else:
            #     self.enemies = get_wave(self.wave)

            current_wave = get_wave(self.wave)
            enemy_spawn_timestamp = time.time()
            spawn_counter = 0

            wave_active = True
            clock = pg.time.Clock()
            while wave_active:
                clock.tick(60)

                # Listen for user input
                for event in pg.event.get():
                    # if event.type == pg.KEYDOWN:
                        # if event.key == pg.K_SPACE:
                        #    wave_active = true
                    if event.type == pg.MOUSEBUTTONDOWN:
                        if event.button == 1:
                            for t in self.towers:
                                if t.hover:
                                    for t_ in self.towers:
                                        t_.selected = False
                                    t.selected = True
                                    self.select_tower(t)
                                    break
                                else:
                                    t.selected = False
                                    self.upgrade_frame.place_forget()
                                    self.root.update()

                # Listen for cursor hover over Tower
                mouse_pos = pg.mouse.get_pos()
                for t in self.towers:
                    if t.rect.collidepoint(mouse_pos):
                        t.hover = True
                    else:
                        t.hover = False

                # Tower Regen
                for t in self.towers:
                    t.health = min(t.health + t.regen / 100.0, t.max_health)

                # Spawn Enemies
                if spawn_counter < len(current_wave):
                    if time.time() - enemy_spawn_timestamp > 0.1:  # 0.1 represents time between enemy spawns in seconds
                        enemy_spawn_timestamp = time.time()
                        key = current_wave[spawn_counter]
                        spawn_counter += 1
                        # print(key)
                        if key == " ":
                            pass
                        else:
                            tower_type = {"o": Orc, "t": Tank, "b": BigBad}[key]
                            self.enemies.append(tower_type(V2(self.map.map_pixels[0]) - V2(tower_type.center_pos), (0,0)))
                in_range = []
                in_range_sniper = []
                # Tower - Enemy interaction
                for t in self.towers:
                    if time.time() - t.last_attack_time > t.cooldown:
                    
                        for e in self.enemies:
                            if not (min(e.pos) < 0 or e.pos.x > 1400 * widthRatio or e.pos.y > 900 * heightRatio):  # Check if enemy is in room
                                distance = t.base_center.distance_to(e.get_center())
                                if distance < t.range:
                                    in_range.append((e, distance))
                                    in_range_sniper.append((e, distance))
                                
                        target = None
                        #maybe# re-order in_range for distance traveled
                        
                        if isinstance(t, Sniper):
                            if len(in_range_sniper) != 0:
                                if t.aim_mode == "first":
                                    target = max(in_range_sniper, key=lambda x: x[0].distance_traveled)[0]
                                elif t.aim_mode == "last":
                                    target = min(in_range_sniper, key=lambda x: x[0].distance_traveled)[0]
                                elif t.aim_mode == "closest":
                                    target = min(in_range_sniper, key=lambda x: x[1])[0]
                                elif t.aim_mode == "strongest":
                                    target = max(in_range_sniper, key=lambda x: x[0].health)[0]
                                t.last_attack_time = time.time()
                                
                                
                                # Aim Projectile at Enemy
                                displacement = target.get_center() - t.base_center
                                displacement += displacement.length() / t.projectile.speed * target.vel  # account for target motion
                                vel = (displacement / displacement.length()) * t.projectile.speed  # scale unit vector
                                proj = t.projectile(t.base_center - t.projectile.center_pos, vel, t.damage)
                                proj.associate(t)
                                proj.enassociate(in_range_sniper[len(in_range_sniper)-1][0])
                                self.projectiles.append(proj)
                        else:
                            if len(in_range) != 0:
                                if t.aim_mode == "first":
                                    target = max(in_range, key=lambda x: x[0].distance_traveled)[0]
                                elif t.aim_mode == "last":
                                    target = min(in_range, key=lambda x: x[0].distance_traveled)[0]
                                elif t.aim_mode == "closest":
                                    target = min(in_range, key=lambda x: x[1])[0]
                                elif t.aim_mode == "strongest":
                                    target = max(in_range, key=lambda x: x[0].health)[0]
                                t.last_attack_time = time.time()
                                # Aim Projectile at Enemy
                                displacement = target.get_center() - t.base_center
                                displacement += displacement.length() / t.projectile.speed * target.vel  # account for target motion
                                vel = (displacement / displacement.length()) * t.projectile.speed  # scale unit vector
                                proj = t.projectile(t.base_center - t.projectile.center_pos, vel, t.damage)
                                proj.associate(t)
                                proj.enassociate(in_range[len(in_range)-1][0])
                                self.projectiles.append(proj)
                                in_range=[]

                # Projectile - Enemy collision
                for p in self.projectiles:
                    for e in self.enemies:
                        if e.health <= 0:
                            self.projectiles.remove(p)
                        if p.get_rect().colliderect(e.get_rect()):
                            self.projectiles.remove(p)
                            e.health -= p.damage
                            # ind2 = in_range.index(e)
                            if e.health <= 0:
                                if isinstance(e, Tank):
                                    indx = self.enemies.index(e)
                                    self.enemies.insert(indx, Orc(e.pos, e.vel))
                                    self.enemies[indx].distance_traveled = e.distance_traveled
                                    self.enemies.insert(indx, Orc(e.pos - V2(1, 1), e.vel))
                                    self.enemies[indx].distance_traveled = e.distance_traveled
                                    self.enemies.sort(key=lambda e: e.distance_traveled)
                                if isinstance(e, BigBad):
                                    indx = self.enemies.index(e)
                                    self.enemies.insert(indx, Tank(e.pos, e.vel))
                                    self.enemies[indx].distance_traveled = e.distance_traveled
                                    self.enemies.insert(indx, Tank(e.pos - V2(1, 1), e.vel))
                                    self.enemies[indx].distance_traveled = e.distance_traveled
                                    self.enemies.sort(key=lambda e: e.distance_traveled)
                                # for t in self.towers:
                                #        distance = t.base_center.distance_to(e.get_center())
                                #        distance1 = t.base_center.distance_to(e.get_center())  
                                #        in_range.insert(ind2, (self.enemies[indx + 1], distance))
                                #        in_range.insert(ind2, (self.enemies[indx + 2], distance1))                              
                                self.enemies.remove(e)
                                self.money += e.value  # Collect value of enemy
                                p.tower.kills += 1  # Iterate tower kill counter
                                self.update_labels()
                                '''if len(self.projectiles) >0:
                                    self.projectiles.remove(p)'''
                                
                            break

                # Enemy movement - OLD
                # for e in self.enemies:
                #     e.pos += e.vel
                #     # TEMPORARY wall collision
                #     if (e.vel.x > 0) == (e.pos.x - 700 > 0):                                    # Allow enemies to enter
                #         if e.pos.x < 0 or e.pos.x > 1400 - e.get_rect().width: e.vel.x *= -1
                #     if (e.vel.y > 0) == (e.pos.y - 450 > 0):                                    # Allow enemies to enter
                #         if e.pos.y < 0 or e.pos.y > 900 - e.get_rect().height: e.vel.y *= -1
                #
                #     # Enemy - Tower collision
                #     e_rect = e.get_rect()
                #     for t in self.towers:
                #         if e_rect.colliderect(t.rect):
                #             e.vel = V2((0, 0))
                #             if time.time() - e.last_attack_time > e.cooldown:
                #                 e.last_attack_time = time.time()
                #                 t.health -= e.damage
                #                 if t.health <= 0:
                #                     self.towers.remove(t)
                #                     self.money += t.get_loot_value()
                #                     self.update_labels()
                #                     for e_ in self.enemies:
                #                         if e_.get_rect().colliderect(t.rect):
                #                             e_.vel = e.starting_vel
                #
                #     # Enemy - Base interaction
                #     if e_rect.colliderect(self.base.rect):
                #         e.vel = V2((0, 0))
                #         if time.time() - e.last_attack_time > e.cooldown:
                #             self.base.health -= e.damage
                #             if self.base.health <= 0:
                #                 wave_active = False
                #                 # TODO: Add death screen

                # Enemy Movement - NEW
                for e in self.enemies:
                    '''if e.vel == V2((0,0)):
                        e.vel = V2(self.map.map_pixels[1]) - V2(self.map.map_pixels[0])
                        e.vel = e.vel / e.vel.length() * e.speed'''
                    e.pos += e.vel
                    e.distance_traveled += e.speed
                    # Turn at map corner
                    for i in range(len(self.map.map_pixels) - 1):
                        if e.get_center().distance_to(V2(self.map.map_pixels[i])) < e.speed + 1:
                            e.vel = V2(self.map.map_pixels[i + 1]) - V2(self.map.map_pixels[i])
                            e.vel = e.vel / e.vel.length() * e.speed  # scale unit vector

                    # Enemy - Base interaction
                    if e.get_rect().colliderect(self.base.rect):
                        '''''e.vel = V2((0, 0))
                        if time.time() - e.last_attack_time > e.cooldown:
                            self.base.health -= e.damage
                            if self.base.health <= 0:
                                wave_active = False'''
                        self.base.health -= e.damage #made it so the health bar on top of the tower decreases as your health decreases.
                        self.health -= e.damage
                        self.enemies.remove(e)
                        self.update_labels()
                    
                        if self.health <=0:
                            self.alive =False
                            self.enemies = []
                            '''break
                        else:
                            continue
                        break
                    else:
                        continue
                    break'''
            
        
                self.enemies.sort(key=lambda e: e.distance_traveled)  # Sort enemies for proper rendering order

                # Projectile movement
                for p in self.projectiles:
                    p.pos += p.vel
                    # if p.pos.x < 0 or p.pos.x > 1400 - p.get_rect().width: p.vel.x *= -1        # TEMPORARY wall collision
                    # if p.pos.y < 0 or p.pos.y > 900 - p.get_rect().height: p.vel.y *= -1        # TEMPORARY wall collision
                    if max(p.pos) > 2000 or min(p.pos) < -100:
                        self.projectiles.remove(p)

                # Check for enemy depletion
                if len(self.enemies) == 0 and len(current_wave) == spawn_counter:
                    wave_active = False

                try:
                    self.root.update()
                except:
                    return
                self.update_screen()
                pg.display.update()

            for t in self.towers:
                t.health = t.max_health
            #self.base.health = self.base.max_health
            self.enemies = []
            self.projectiles = []
            self.update_screen()
            pg.display.update()
        
            self.health=self.health
            self.wave += 1
            self.wave_button["text"] = "wave {0}\nstart".format(self.wave)
            self.wave_button["state"] = "normal"
        
def main():
    logf = open("Log.log", "a+")
    game = GameTop()
    try:
        game.mainloop()
        logf.write("I completed the game this date & time: " + str(datetime.now()) + "\n\n")

    except Exception as e:
        logf.write(str(e) + " date & time: " + str(datetime.now()) + "\n\n")


if __name__ == "__main__":
    main()
