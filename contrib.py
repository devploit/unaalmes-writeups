import os
import urllib.parse


def create_contribs():
    contributions = dict()
    for challenge in os.scandir('writeups/'):
        if challenge not in contributions:
            contributions[challenge] = dict()
        for episode in os.scandir('writeups/{}/'.format(challenge.name)):
            if episode not in contributions[challenge]:
                contributions[challenge][episode] = []
            for user in os.scandir('writeups/{}/{}/'.format(challenge.name, episode.name)):
                contributions[challenge][episode].append(user.name)
    return contributions


def contrib_rankings(contribs):
    ranking = dict()
    for challenge in contribs:
        for episode in contribs[challenge]:
            for user in contribs[challenge][episode]:
                if user not in ranking:
                    ranking[user] = 1
                else:
                    ranking[user] += 1
    return ranking


def md_template_ranking(ranking):
    print("# Contributors")
    rank_md_row = "| {} | {} | {} |"
    print("| # | Nickname | Contributions |")
    print("|---|---|---:|")
    row = 1
    for user in sorted(ranking, key=ranking.__getitem__, reverse=True):
        row_format = rank_md_row.format(row, user, ranking[user])
        print(row_format)
        row += 1


def md_template_contribs(contribs):
    writeups_dir = "writeups"
    github_url_format = "https://github.com/j0n3/unaalmes-writeups/tree/new-contribs-test/{}/{}"
    print("# Challenges")
    sorted_challenges = sorted(contribs, key=lambda x: x.name, reverse=True)
    for challenge in sorted_challenges:
        print("## {}".format(challenge.name))
        print("| Episode | Writeups |")
        print("|---|---|")
        sorted_episodes = sorted(contribs[challenge], key=lambda x: x.name, reverse=False)
        for episode in sorted_episodes:
            print("| **{}:** |".format(episode.name), end="")
            for user in contribs[challenge][episode]:
                params = "{}/{}/{}" \
                    .format(urllib.parse.quote(challenge.name),
                            urllib.parse.quote(episode.name),
                            urllib.parse.quote(user))
                print("[{}]({}) <br>" \
                      .format(user, github_url_format.format(writeups_dir, params), end=""), end="")
            print("|")


if __name__ == '__main__':
    contributors = create_contribs()
    ranking = contrib_rankings(contributors)

    md_template_contribs(contributors)
    md_template_ranking(ranking)
