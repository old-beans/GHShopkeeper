#GHShopkeeper Discord Bot v3.0.1 by Old Beans
#Discord Bot for maintaing character and world stats
#Data stored in Google Sheets.
#v3.0.1 now includes !gethelp, !buy, !sell, !ability
import gspread #Google sheets API, v 3.6.0
import discord #Discord API
import re #regex for parsing
import random #for random numbers
from discord.ext import commands
import fstrings
gc = gspread.service_account()
sh = gc.open("GHStats")
sh_characters = sh.get_worksheet(0) #Characters worksheet location
sh_items = sh.get_worksheet(1) #Items Worksheet location
sh_ref_values = sh.get_worksheet(2) #World Stats Sheet location
pros_up = (0,4,9,15,22,30,39,50,64) #prosperity reference values on the prosperity track.
level_up = (0,45,95,150,210,275,345,420,500) 
discounts_dict = {-20:5,-19:5,
                -18:4,-17:4,-16:4,-15:4,
                -14:3,-13:3,-12:3,-11:3,
                -10:2,-9:2,-8:2,-7:2,
                -6:1,-5:1,-4:1,-3:1,
                -2:0,-1:0,0:0,1:0,2:0,
                3:-1,4:-1,5:-1,6:-1,
                7:-2,8:-2,9:-2,10:-2,
                11:-3,12:-3,13:-3,14:-3,
                15:-4,16:-4,17:-4,18:-4,
                19:-5,20:-5}

client = commands.Bot(command_prefix = "!")

@client.event
async def on_ready():
    await client.change_presence(activity=discord.Activity(name='Test'))
    print('Logged in as {0.user}'.format(client))
@client.command()
async def boobs(ctx):
    await ctx.send("(.)(.)")

@client.command(aliases=['Help'])
async def gethelp(ctx):
    await ctx.send(f"I am the Gloomhaven Shopkeeper. You can do the following:\n**!donate:** Donate 10 gold to the Sanctuary\n**!stats:** get your current stats\n**!stats AAxp BBgp CCch lvX:** Updates your stats. Omit any stats you don't want to update\n**!buy XX:** Adds item XX to your stats\n**!sell XX:** Remove item XX from your stats (does not update your gold)\n**!ability XX:** Adds abillity XX to your stats (does not update your gold)")
@client.command()
async def buy(ctx,*args):
#Add items to the items list
#!buy 1, 4, 62, 23, 188
    author = ctx.message.author.name
    char_cell = sh_characters.find(author)
    char_row = char_cell.row
    items_str = sh_characters.cell(char_row,8).value
    items_list = items_str.split(", ")
    #spreadsheet format show be 'xx, yy, zz'
    for arg in args:
        item = arg.strip(",")
        if item in items_list:
            await ctx.send(f"According to our records you already own {item}.\nYou can only own 1 copy of an item.")
        else:
            items_list.append(item)
            # await ctx.send(f"You purchased {item}")
    items_list.sort(key=int)
    glue = ", "
    items_str = glue.join(items_list)
    sh_characters.update_cell(char_row,8,items_str) 
    discount  = int(sh_ref_values.acell('E2').value)
    await ctx.send(f"Please update your gold manually. Discount: {discount}\nItems: {items_str}")
@client.command()
async def sell(ctx,*args):
#Add items to the items list
#!buy 1, 4, 62, 23, 188
    author = ctx.message.author.name
    char_cell = sh_characters.find(author)
    char_row = char_cell.row
    items_str = sh_characters.cell(char_row,8).value
    items_list = items_str.split(", ")
    for arg in args:
        item = arg.strip(",")
        if item in items_list:
            items_list.remove(item)
            # await ctx.send(f"You sold {item}")
        else:
            await ctx.send(f"According to our records you do not own {item}")
    items_list.sort(key=int)
    glue = ", "
    items_str = glue.join(items_list)
    sh_characters.update_cell(char_row,8,items_str) 
    discount  = int(sh_ref_values.acell('E2').value)
    await ctx.send(f"Sale recorded. Please update your gold manually..\nItems: {items_str}")
@client.command(aliases=['abil'])
async def ability(ctx,*args):
#Add abilities to the ability list
#!buy 1, 4, 62, 23, 188
    author = ctx.message.author.name
    char_cell = sh_characters.find(author)
    char_row = char_cell.row
    abil_str = sh_characters.cell(char_row,9).value
    abil_list = abil_str.split(", ")
    for arg in args:
        abil = arg.strip(",")
        if abil in abil_list:
            pass
        else:
            abil_list.append(abil)
            # await ctx.send(f"You purchased {item}")
    abil_list.sort(key=int)
    glue = ", "
    abil_str = glue.join(abil_list)
    sh_characters.update_cell(char_row,9,abil_str) 
    await ctx.send(f"Abilities Updates: {abil_str}")
@client.command()
async def stats(ctx, *args):
#get or update character stats by Discord username
#update requires this format in Discord "!stats 100xp 100gp 100ch"
    author = ctx.message.author.name
    char_cell = sh_characters.find(author)
    char_row = char_cell.row
    stats = sh_characters.row_values(char_cell.row)
    ch = 'checks'
    if len(args) == 0:
#if no args are entered, only return the current stats
        if int(stats[6])==1:
            ch = 'check'
        await ctx.send(f"**{stats[1]}:--Lv{stats[3]} {stats[2]}**\n{stats[4]}xp {stats[5]}gp {stats[6]}ch\nItems: {stats[7]}\nAbilities: {stats[8]}")
        #returned format matches the requested input format
    elif len(args) > 0:
#input new totals for XP, Gold, Checks and update the master data
        for arg in args:
 #assuming format Xxp Ygold Zchecks -- No Spaces
            if 'lv' in arg:
                lv = int(re.sub("[^0-9]", "", arg))
                sh_characters.update_cell(char_row,4,lv)
            elif 'x' in arg:
                xp = int(re.sub("[^0-9]", "", arg))
                sh_characters.update_cell(char_row,5,xp)
            elif 'g' in arg:
                gold = re.sub("[^0-9]", "", arg)
                sh_characters.update_cell(char_row,6,gold)
            elif 'ch' in arg:
                ch = int(re.sub("[^0-9]", "", arg))
                sh_characters.update_cell(char_row,7,ch)
#There must be a better way, since these expressions are not necessarily regular
        stats = sh_characters.row_values(char_cell.row)
        await ctx.send(f"**{stats[1]}:--Lv{stats[3]} {stats[2]}**\n{stats[4]}xp {stats[5]}gp {stats[6]}ch\nItems: {stats[7]}\nAbilities: {stats[8]}")
@client.command(aliases=["getall","worldstats","campaignstats"])
async def teamstats(ctx):
#Returns the current donations, prosperity, reputation, and store discount
    donations = int(sh_ref_values.acell('A2').value)
    prosperity = int(sh_ref_values.acell('C2').value)
    pticks = int(sh_ref_values.acell('B2').value)
    reputation = int(sh_ref_values.acell('D2').value)
    discount  = int(sh_ref_values.acell('E2').value)
    await ctx.send(f"Donations: {donations}\nProsperity: {prosperity}.....{pticks}/{pros_up[prosperity]}\nRepuation: {reputation}....Discount: {discount}")
@client.command(aliases=["donation","makedonation"])
async def donate(ctx):
#Adds a donation to the total and asjusts player gold.
#+1 propserity tick when appropriate
#+1 overall prosperity when appropriate
#Updates overall propserity when applicable
    author = ctx.message.author.name
    char_cell = sh_characters.find(author)
    char_gold = int(sh_characters.cell(char_cell.row,6).value) - 10
    donations = int(sh_ref_values.acell('A2').value) + 10
    career_donations = int(sh_characters.cell(char_cell.row,16).value) + 10
    sh_ref_values.update('A2', donations)
    sh_characters.update_cell(char_cell.row, 6, char_gold)
#sheet.update for A1 format vs sheet.update_cell for (R,C) format
    await ctx.send(f"The Sanctuary of the Great Oak thanks you. Have a blessed battle!\nDonations: {donations}")
#It always sends this message immediately and then determines if properity should be updated
    if donations % 50 == 0: #+1 pros for every 50 donation
        pticks = int(sh_ref_values.acell('B2').value) #individual tick boxes along the prosperity track
        pticks += 1
        sh_ref_values.update('B2', pticks)
        prosperity = int(sh_ref_values.acell('C2').value) #Overall Gloomhaven Propserity (affects item stores, character level, enhancement limit)
        await ctx.send("+1 Prosperity.....%s/%s" %(pticks,pros_up[prosperity]))
        if pticks in pros_up:
            prosperity += 1
            sh_ref_values.update('C2', prosperity)
            await ctx.send("Gloomhaven Prosperity has increased to %s!!\nNew Items Available!!\nCharacters may level-up to Lv %s on next visit to Gloomhaven") % prosperity
@client.command(aliases=['undonate','removedonation'])
async def canceldonation(ctx):
#subtracts a mistaken donation
#does not currently check and update prosperity.
    author = ctx.message.author.name
    char_cell = sh_characters.find(author)
    donations = int(sh_ref_values.acell('A2').value) + 10   
    char_gold = int(sh_characters.cell(char_cell.row,6).value) - 10
    sh_ref_values.update('A2', donations)   
    sh_ref_values.update_cell(char_cell.row,6, char_gold)
    await ctx.send("Donations: %s" % donations)
#fix it to adjust prosperity
#It should check donations and pticks before updating ie if pticks in pros_up lower overall prosperity and then update p-ticks cell
@client.command(aliases=['+pros',"gainpros"])
async def addpros(ctx):
#adds 1 to pticks ... in game "Gain 1 Prosperity"
    prosperity = int(sh_ref_values.acell('C2').value)
    pticks = int(sh_ref_values.acell('B2').value)
    pticks += 1
    await ctx.send(f"+1 Prosperity.....{pticks}/{pros_up[prosperity]}")
    sh_ref_values.update('B2', pticks)
    if pticks in pros_up:
    #increase the overall prosperity when the next threshold is reached
        prosperity += 1
        sh_ref_values.update('C2', prosperity)
        await ctx.send(f"Gloomhaven Prosperity has increased to {prosperity}!!\nNew Items Available!!\nCharacters may level-up to Lv{prosperity} on next visit to Gloomhaven")
@client.command()
async def losepros(ctx):
#subtracts 1 from pticks ... in game "Lose 1 Prosperity"
    pticks = int(sh_ref_values.acell('B2').value)
    prosperity = int(sh_ref_values.acell('C2').value)
    if pticks in pros_up:
        await ctx.send(f"Prosperity cannot be decreased beyond {pticks}")
    else:
        pticks -= 1
        sh_ref_values.update('B2', pticks)
        await ctx.send(f"-1 Prosperity.....{pticks}/{pros_up[prosperity]}")
@client.command()
async def addrep(ctx):
#Adds 1 to party reputation ... in game "Gain 1 Reputation"
#Will need updating if a second party is ever formed
    reputation = int(sh_ref_values.acell('D2').value) #party reputation.
    reputation += 1 #These edits could easily just go in the line above
#it felt easier to create a dictionary this way, rather than entering the whole thing long-form
    discount = discounts_dict[int(reputation)]
    sh_ref_values.update('D2', reputation)
    sh_ref_values.update('E2', discount)
    await ctx.send(f"Wyld Stallyns Reputation: {reputation}.....Discount: {discount}")
@client.command()
async def loserep(ctx):
#In game "Lose 1 reputation"
    reputation = int(sh_ref_values.acell('D2').value)
    reputation -= 1
#creating the dictionary multiple times makes no sense. Should be moved to the top.
    discount = discounts_dict[int(reputation)]
    sh_ref_values.update('D2', reputation)
    sh_ref_values.update('E2', discount)
    await ctx.send(f"Wyld Stallyns Reputation: {reputation}.....Discount: {discount}")

client.run('NzEzMDk1NjgwMzQzOTMyOTg4.Xuw6KQ.77mANY8h54vwkuJbQX1jq07KQVw')
#How can I keep the token discreet?
