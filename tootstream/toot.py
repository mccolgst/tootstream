import os.path
import click
import readline
import getpass
import sys
import re
from mastodon import Mastodon
from collections import OrderedDict

# TODO: need to modify this to support multiple shards, since we have to
# register per shard.
# For now it only supports the default mastodon.social shard.
APP_PATH = os.path.expanduser('~/.config/tootstream/client.txt')
APP_CRED = os.path.expanduser('~/.config/tootstream/token.txt')


def register_app():
    if not os.path.exists(os.path.expanduser('~/.config/tootstream')):
        os.makedirs(os.path.expanduser('~/.config/tootstream'))
    if os.path.isfile(APP_PATH):
        return
    Mastodon.create_app(
        'tootstream',
        to_file=APP_PATH
    )


def login(mastodon, email, password, shard=None):
    """
    Login to the mastodon.social shard.
    Return a Mastodon client if login success, otherwise returns None.
    """
    mastodon.log_in(
        email,
        password,
        to_file = APP_CRED
    )

#####################################
######## BEGIN COMMAND BLOCK ########
#####################################


commands = OrderedDict()
def command(func):
    commands[func.__name__] = func
    return func


@command
def help(mastodon, rest):
    """List all commands."""
    print("Commands:")
    for command, cmd_func in commands.items():
        print("\t{}\t{}".format(command, cmd_func.__doc__))


@command
def toot(mastodon, rest):
    """Publish a toot. ex: 'toot Hello World' will publish 'Hello World'."""
    mastodon.toot(rest)
    print("Published: " + rest)


@command
def boost(mastodon, rest):
    """Boosts a toot by ID."""
    # TODO catch if boost is not a real ID
    mastodon.status_reblog(rest)
    boosted = mastodon.status(rest)
    print("  Boosted: " + re.sub('<[^<]+?>', '', boosted['content']))


@command
def unboost(mastodon, rest):
    """Removes a boosted tweet by ID."""
    # TODO catch if uboost is not a real ID
    mastodon.status_unreblog(rest)
    unboosted = mastodon.status(rest)
    print("  Removed boost: " + re.sub('<[^<]+?>', '', unboosted['content']))


@command
def fav(mastodon, rest):
    """Favorites a toot by ID."""
    # TODO catch if fav is not a real ID
    mastodon.status_favourite(rest)
    faved = mastodon.status(rest)
    print("  Favorited: " + re.sub('<[^<]+?>', '', faved['content']))


@command
def unfav(mastodon, rest):
    """Removes a favorite toot by ID."""
    # TODO catch if ufav is not a real ID
    mastodon.status_unfavourite(rest)
    unfaved = mastodon.status(rest)
    print("  Removed favorite: " + re.sub('<[^<]+?>', '', unfaved['content']))


@command
def home(mastodon, rest):
    """Displays the Home timeline."""
    for toot in reversed(mastodon.timeline_home()):
        display_name = "  " + toot['account']['display_name']
        username = " @" + toot['account']['username'] + " "
        reblogs_count = "  ♺:" + str(toot['reblogs_count'])
        favourites_count = " ♥:" + str(toot['favourites_count']) + " "
        toot_id = str(toot['id'])

        # Prints individual toot/tooter info
        print(display_name + username + toot['created_at'])
        print(reblogs_count + favourites_count + toot_id)

        # shows boosted toots as well
        if toot['reblog']:
            username = "  Boosted @" + toot['reblog']['account']['username']
            display_name = toot['reblog']['account']['display_name'] + ": "
            clean = re.sub('<[^<]+?>', '', toot['reblog']['content'])
            content = username + display_name + clean

        # TODO: Toots with only HTML do not display (images, links)
        # TODO: Breaklines should be displayed correctly
        content = "  " + re.sub('<[^<]+?>', '', toot['content'])
        print(content + "\n")


@command
def public(mastodon, rest):
    """Displays the Public timeline."""
    for toot in reversed(mastodon.timeline_public()):
        display_name = "  " + toot['account']['display_name']
        username = " @" + toot['account']['username'] + " "
        reblogs_count = "  ♺:" + str(toot['reblogs_count'])
        favourites_count = " ♥:" + str(toot['favourites_count']) + " "
        toot_id = str(toot['id'])

        # Prints individual toot/tooter info
        print(display_name + username + toot['created_at'])
        print(reblogs_count + favourites_count + toot_id)


        # shows boosted toots as well
        if toot['reblog']:
            username = "  Boosted @" + toot['reblog']['account']['username']
            display_name = toot['reblog']['account']['display_name'] + ": "
            clean = re.sub('<[^<]+?>', '', toot['reblog']['content'])
            content = username + display_name + clean

        # TODO: Toots with only HTML do not display (images, links)
        # TODO: Breaklines should be displayed correctly
        content = "  " + re.sub('<[^<]+?>', '', toot['content'])
        print(content + "\n")

@command
def note(mastodon, rest):
    """Displays the Notifications timeline."""
    for note in reversed(mastodon.notifications()):
        display_name = "  " + note['account']['display_name']
        username = " @" + note['account']['username']


        # Mentions
        if note['type'] == 'mention':
            print(display_name + username)
            print("  " + re.sub('<[^<]+?>', '', note['status']['content']))

        # Favorites
        elif note['type'] == 'favourite':
            reblogs_count = "  " + "♺:" + str(note['status']['reblogs_count'])
            favourites_count = " ♥:" + str(note['status']['favourites_count'])
            time = " " + note['status']['created_at']
            content = "  " + re.sub('<[^<]+?>', '', note['status']['content'])

            print(display_name + username + " favorited your status:")
            print(reblogs_count + favourites_count + time + '\n' + content)

        # Boosts
        elif note['type'] == 'reblog':
            print(display_name + username + " boosted your status:")
            print("  " + re.sub('<[^<]+?>', '', note['status']['content']))

        # Follows
        elif note['type'] == 'follow':
            username = re.sub('<[^<]+?>', '', username)
            print(display_name + username + " followed you!")

        # blank line
        print('')


@command
def quit(mastodon, rest):
    """Ends the program."""
    sys.exit("Goodbye!")


@command
def info(mastodon, rest):
    """Prints your user info."""
    user = mastodon.account_verify_credentials()

    print("@" + str(user['username']))
    print(user['display_name'])
    print(user['url'])
    print(re.sub('<[^<]+?>', '', user['note']))


@command
def delete(mastodon, rest):
    """Deletes your toot by ID"""
    mastodon.status_delete(rest)
    print("Poof! It's gone.")

@command
def block(mastodon, rest):
    """Blocks a user by username."""
    # TODO: Find out how to get global usernames

@command
def unblock(mastodon, rest):
    """Unblocks a user by username."""
    # TODO: Find out how to get global usernames

@command
def follow(mastodon, rest):
    """Follows an account by username."""
    # TODO: Find out how to get global usernames

@command
def unfollow(mastodon, rest):
    """Unfollows an account by username."""
    # TODO: Find out how to get global usernames



#####################################
######### END COMMAND BLOCK #########
#####################################


def authenticated(mastodon):
    if not os.path.isfile(APP_CRED):
        return False
    if mastodon.account_verify_credentials().get('error'):
        return False
    return True


@click.command()
@click.option('--email')
@click.option('--password')
def main(email, password):
    register_app()

    mastodon = Mastodon(client_id=APP_PATH, access_token=APP_CRED)

    if email and password:
        login(mastodon, email, password)
    elif not authenticated(mastodon):
        email = input("Email used to login: ")
        password = getpass.getpass()
        login(mastodon, email, password)

    say_error = lambda a, b: print("Invalid command. Use 'help' for a \
                                    list of commands.")

    print("Welcome to tootstream!")
    print("Enter a command. Use 'help' for a list of commands.")
    print("\n")

    user = mastodon.account_verify_credentials()
    prompt = "[@" + str(user['username']) + "]: "

    while True:
        command = input(prompt).split(' ', 1)
        rest = ""
        try:
            rest = command[1]
        except IndexError:
            pass
        command = command[0]
        cmd_func = commands.get(command, say_error)
        cmd_func(mastodon, rest)

if __name__ == '__main__':
    main()
