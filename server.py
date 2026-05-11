#!/usr/bin/env python3
import http.server
import socketserver
import urllib.request
import re
import os
import json
import math
import argparse
from html.parser import HTMLParser

PORT = 8080
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

WORLD_SOURCES = {
    'swiss': [
        {'name': '20min.ch', 'url': 'https://www.20min.ch'},
        {'name': 'SRF.ch', 'url': 'https://www.srf.ch/news'},
        {'name': 'NZZ.ch', 'url': 'https://www.nzz.ch'},
        {'name': 'Watson.ch', 'url': 'https://www.watson.ch'},
        {'name': 'LeTemps.ch', 'url': 'https://www.letemps.ch'},
        {'name': 'Handelszeitung.ch', 'url': 'https://www.handelszeitung.ch'},
        {'name': 'Aargauer.ch', 'url': 'https://www.aargauerzeitung.ch'},
        {'name': 'Luzerner Zeitung', 'url': 'https://www.luzernerzeitung.ch'},
    ],
    'world': [
        {'name': 'BBC', 'url': 'https://www.bbc.com/news'},
        {'name': 'CNN', 'url': 'https://www.cnn.com'},
        {'name': 'CBS News', 'url': 'https://www.cbsnews.com'},
        {'name': 'NYT', 'url': 'https://www.nytimes.com'},
        {'name': 'The Guardian', 'url': 'https://www.theguardian.com'},
        {'name': 'Al Jazeera', 'url': 'https://www.aljazeera.com'},
        {'name': 'DW', 'url': 'https://www.dw.com'},
        {'name': 'ABC News', 'url': 'https://abcnews.go.com'},
        {'name': 'MSNBC', 'url': 'https://www.msnbc.com'},
        {'name': 'France24', 'url': 'https://www.france24.com'},
        {'name': 'The Independent', 'url': 'https://www.independent.co.uk'},
    ]
}

SPORTS_SOURCES = {
    'swiss': [
        {'name': 'SRF Sport', 'url': 'https://www.srf.ch/sport'},
        {'name': 'Watson Sport', 'url': 'https://www.watson.ch/sport'},
        {'name': 'Hockeyinfo', 'url': 'https://www.hockeyinfo.ch'},
        {'name': 'Nau.ch Sport', 'url': 'https://www.nau.ch/sport'},
    ],
    'global': [
        {'name': 'ESPN', 'url': 'https://www.espn.com'},
        {'name': 'BBC Sport', 'url': 'https://www.bbc.com/sport'},
        {'name': 'Sky Sports', 'url': 'https://www.skysports.com'},
        {'name': 'The Athletic', 'url': 'https://www.theathletic.com'},
        {'name': 'Yahoo Sports', 'url': 'https://sports.yahoo.com'},
        {'name': 'Sportskeeda', 'url': 'https://www.sportskeeda.com'},
        {'name': 'CBS Sports', 'url': 'https://www.cbssports.com'},
        {'name': 'NFL', 'url': 'https://www.nfl.com'},
        {'name': 'Pro Football', 'url': 'https://www.pro-football-reference.com'},
        {'name': 'NBA', 'url': 'https://www.nba.com'},
        {'name': 'EuroLeague', 'url': 'https://www.euroleaguebasketball.com'},
        {'name': 'NHL', 'url': 'https://www.nhl.com'},
        {'name': 'IIHF', 'url': 'https://www.iihf.com'},
        {'name': 'MLB', 'url': 'https://www.mlb.com'},
        {'name': 'F1', 'url': 'https://www.formula1.com'},
        {'name': 'WRC', 'url': 'https://www.wrc.com'},
        {'name': 'MotoGP', 'url': 'https://www.motogp.com'},
        {'name': 'ATP Tennis', 'url': 'https://www.atptour.com'},
        {'name': 'WTA Tennis', 'url': 'https://www.wtatennis.com'},
        {'name': 'ProCyclingStats', 'url': 'https://www.procyclingstats.com'},
        {'name': 'Cyclingnews', 'url': 'https://www.cyclingnews.com'},
        {'name': 'FIFA', 'url': 'https://www.fifa.com'},
        {'name': 'UEFA', 'url': 'https://www.uefa.com'},
        {'name': 'PDC Darts', 'url': 'https://www.pdc.tv'},
        {'name': 'World Snooker', 'url': 'https://www.worldsnookerdata.com'},
        {'name': 'PGA Tour', 'url': 'https://www.pgatour.com'},
        {'name': 'LPGA', 'url': 'https://www.lpga.com'},
        {'name': 'Olympics', 'url': 'https://olympics.com'},
        {'name': 'WSL', 'url': 'https://www.womenssuperleague.com'},
        {'name': 'UWCL', 'url': 'https://www.uefa.com/uefwomenwschampionsleague/'},
        {'name': 'NWSL', 'url': 'https://www.nwslsoccer.com'},
        {'name': 'WNBA', 'url': 'https://www.wnba.com'},
        {'name': 'PWHL', 'url': 'https://www.thepwhl.com'},
        {'name': 'UCI Women', 'url': 'https://www.uci.org/women-cycling'},
        {'name': 'World Athletics', 'url': 'https://worldathletics.org'},
    ]
}

POSITIVE_WORDS = {
    'happy', 'joy', 'love', 'great', 'amazing', 'wonderful', 'excellent', 'fantastic', 'good', 'best',
    'beautiful', 'success', 'successful', 'victory', 'won', 'winner', 'celebrate', 'celebration', 'hope',
    'hopeful', 'positive', 'peace', 'peaceful', 'progress', 'improvement', 'growth', 'growing',
    'achievement', 'accomplish', 'grateful', 'thank', 'thanks', 'appreciate', 'brilliant', 'perfect',
    'outstanding', 'incredible', 'inspiring', 'excited', 'delighted', 'delight', 'congratulations', 'congrats',
    'win', 'winning', 'champion', 'hero', 'heroes', 'brave', 'courage', 'support', 'unite', 'together',
    'strong', 'strength', 'healthy', 'safe', 'helpful', 'kind', 'generous', 'smile', 'laugh', 'fun',
    'enjoy', 'welcome', 'exciting', 'thrilled', 'blessed', 'lucky', 'proud', 'honor', 'achieve',
    'dream', 'goals', 'beneficial', 'useful', 'effective', 'efficient', 'resolve', 'resolved',
    'breakthrough', 'cure', 'vaccine', 'recovery', 'improve', 'launch', 'launches', 'announce',
    'announces', 'historic', 'milestone', 'record', 'surge', 'soars', 'gains', 'rises', 'upbeat'
}

NEGATIVE_WORDS = {
    'sad', 'unhappy', 'angry', 'hate', 'terrible', 'awful', 'horrible', 'worst', 'bad', 'failure',
    'failed', 'lose', 'lost', 'loss', 'death', 'died', 'dead', 'die', 'crisis', 'disaster', 'tragedy',
    'tragic', 'fear', 'afraid', 'scared', 'horror', 'terrified', 'panic', 'worry', 'worried', 'anxious',
    'anxiety', 'stress', 'stressed', 'depressed', 'depression', 'pain', 'painful', 'suffer', 'suffering',
    'hurt', 'injury', 'injured', 'wound', 'violence', 'violent', 'attack', 'attacked', 'threat',
    'threaten', 'danger', 'dangerous', 'problem', 'problems', 'issue', 'issues', 'fail', 'fails',
    'failing', 'mistake', 'mistakes', 'wrong', 'error', 'errors', 'criticize', 'criticism', 'warn',
    'warning', 'warnings', 'alert', 'alerts', 'emergency', 'urgent', 'breaking', 'bomb', 'shooting', 'shot',
    'killed', 'killing', 'murder', 'accident', 'crash', 'conflict', 'war', 'fighting', 'fight',
    'protest', 'protests', 'arrest', 'arrested', 'scandal', 'fraud', 'fake', 'lies', 'lie', 'lying',
    'denied', 'deny', 'refuse', 'refused', 'reject', 'rejected', 'cancel', 'cancelled', 'delay', 'delayed',
    'postpone', 'postponed', 'suspended', 'shutdown', 'close', 'closed', 'bankrupt', 'bankruptcy',
    'layoff', 'layoffs', 'fired', 'resign', 'resigned', 'quit', 'concern', 'concerned', 'doubt',
    'doubtful', 'suspicious', 'uncertain', 'collapses', 'collide', 'explosion', 'outbreak', 'plague',
    'pandemic', 'epidemic', 'quarantine', 'lockdown', 'inflation', 'recession', 'decline', 'crash',
    'bankrun', 'defeat', 'defeated', 'flee', 'fled', 'refugee', 'humanitarian', 'catastrophe'
}

BREAKING_KEYWORDS = {
    'breaking', 'urgent', 'emergency', 'live', 'developing', 'just in', 'alert', 'declaration',
    'declaration of war', 'attack', 'attacked', 'explosion', 'shooting', 'casualties'
}

HIGH_HEAT_KEYWORDS = {
    'finals', 'final', 'championship', 'game 7', 'playoffs', 'playoff', 'derbies', 'derby',
    'cup', 'semi-final', 'semifinal', 'title decider', 'decider', 'super bowl', 'stanley cup',
    'world series', 'euro cup', 'rivalry', 'battle', 'championships', 'finale',
    'finale', 'finalspiel', 'finals', 'meister', 'meisterchaft', 'champion', 'championat',
    'playoffs', 'playoff', 'puck', 'cup', 'pokal', 'schweizer cup', 'nations league',
    'derby', 'rivalen', 'rivalität', 'kampf', 'schlacht', 'duell',
    'halbfinale', 'semifinal', 'viertelfinale', 'quarters',
    'entscheidung', 'entscheidend', 'titelkampf', 'tittelsieg',
    'super bowl', 'stanley cup', 'world series', 'euro cup',
    'nla', 'nlb', 'nlk', 'national league', 'swiss league',
    'Ambri-Piotta', 'Ambri', 'Piotta', 'ZSC Lions', 'Davos', 'Lugano',
    'Zug', 'Bern', 'Fribourg', 'Lausanne', 'Genf', 'EHC Kloten',
    'eishockey', 'hockey', 'nhl',
    'super league', 'challenge league', 'fcl', 'fcb', 'fcz', 'gc',
    'YB', 'BSC Young Boys', 'Servette', 'Grasshopper',
    'tour de france', 'tour de suisse', 'tour of switzerland', 'giro d\'italia', 'giro', 'vuelta a espana', 'vuelta',
    'milan-san remo', 'milano-san remo', 'paris-roubaix', 'tour of flandres', 'tour des flandres',
    'liege-bastogne-liege', 'il lombardia', 'lombardia', 'strade bianche', 'klassiker',
    'olympia', 'olympisch', 'olympics', 'wintergames', 'sommergames',
    'weltcup', 'world cup', 'abfahrt', 'slalom', 'super-g', 'riesenslalom'
}

SPORT_WEIGHTS = {
    'hockey': 3, 'eishockey': 3,
    'nhl': 3, 'iihf': 3, 'nla': 3, 'nlb': 3, 'nlk': 3,
    'swiss league': 3, 'national league': 3,
    'ambri-piotta': 4, 'ambri': 4, 'piotta': 4,
    'davos': 3, 'zsc lions': 3, 'zug': 3, 'bern': 3, 'fribourg': 3, 'lugano': 3, 'lausanne': 3, 'genf': 3, 'geneva': 3,
    'cycling': 3, 'radfahren': 3, 'radsport': 3,
    'tour de france': 3, 'tour de suisse': 4, 'tour of switzerland': 4,
    'giro': 3, 'giro d\'italia': 3, 'vuelta': 3, 'vuelta a espana': 3,
    'milan-san remo': 3, 'milano-san remo': 3, 'paris-roubaix': 3, 'tour of flanders': 3, 'tour des flandres': 3,
    'liege-bastogne-liege': 3, 'lombardia': 3, 'il lombardia': 3, 'strade biane': 3,
    'wrc': 2, 'rally': 2,
    'nfl': 2, 'american football': 2,
    'super league': 3, 'challenge league': 2.5, 'fcl': 3, 'fcb': 3, 'fcz': 3, 'gc': 3, 'yb': 3, 'servette': 3, 'grasshopper': 3,
    'football': 1.5, 'soccer': 1.5, 'fussball': 1.5,
    'premier league': 1.5, 'bundesliga': 1.5, 'la liga': 1.5, 'serie a': 1.5,
    'champions league': 1.5, 'europa league': 1.5,
    'nba': 1.5, 'basketball': 1.5,
    'f1': 1.5, 'formula 1': 1.5, 'motogp': 1.5,
    'tennis': 1, 'golf': 1, 'baseball': 1, 'mlb': 1,
    'snooker': 1, 'darts': 1, 'ski': 2, 'skiing': 2, 'alpine': 2,
}

EVENT_TYPE_WEIGHTS = {
    'final': 3, 'finals': 3, 'finale': 3, 'finalspiel': 3,
    'championship': 3, 'meister': 3, 'meisterchaft': 3,
    'game 7': 3, 'decider': 3, 'title decider': 3,
    'derby': 2, 'derbies': 2, 'rivalry': 2, 'rivalen': 2,
    'semi-final': 2, 'semifinal': 2, 'halbfinale': 2,
    'playoffs': 2, 'playoff': 2, 'postseason': 2,
    'qualifier': 1.5, 'qualifikation': 1.5,
    'transfer': 1.5, 'transfers': 1.5,
    'stage win': 2, 'stage victory': 2, 'etappensieg': 2,
    'mountain stage': 2, 'bergwertung': 2,
    'time trial': 2, 'zeitfahren': 2, 'contre-la-montre': 2,
    'sprint': 1.5, 'sprint finish': 1.5,
    'leader': 1.5, 'leader jersey': 2, 'yellow jersey': 2, 'maglia gialla': 2,
    'gc': 2, 'general classification': 2,
    'rumor': 0.5, 'rumours': 0.5, 'gerücht': 0.5,
    'training': 0.5, 'trainieren': 0.5,
}

SPORTS_POSITIVE = {
    'win', 'winner', 'winning', 'won', 'victory', 'champion', 'champions', 'championship',
    'title', 'trophy', 'cup', 'pokal', 'triumph', 'top', 'lead', 'leading',
    'score', 'scored', 'goal', 'goals', 'hat-trick', 'brace', 'assist',
    'podium', 'pole', 'pole position', 'race win', 'fastest', 'record',
    'promoted', 'promotion', 'return', 'returning', 'back', 'comeback',
    'signs', 'signing', 'new contract', 'extend', 'extended',
    'best', 'top', 'great', 'amazing', 'incredible', 'historic',
}

SPORTS_NEGATIVE = {
    'loss', 'lost', 'lose', 'defeat', 'defeated', 'losses',
    'eliminated', 'knocked out', 'out', 'exit', 'exits',
    'relegated', 'relegation', 'drop', 'dropped',
    'sacked', 'fired', 'resign', 'resigned', 'quit',
    'injury', 'injured', 'injuries', 'out injured', 'doubtful',
    'crash', 'crashed', 'dnf', 'did not finish', 'dsq', 'disqualified',
    'red card', 'sent off', 'dismissed', 'suspended',
    'penalty', 'own goal', 'miss', 'missed', 'blown', 'blew',
    'worst', 'bad', 'terrible', 'humiliation', 'humiliating',
}

STATS_SITES = {
    'Football': [
        {'name': 'Flashscore', 'url': 'https://www.flashscore.com'},
        {'name': 'SofaScore', 'url': 'https://www.sofascore.com'},
        {'name': 'FootyStats', 'url': 'https://www.footystats.org'},
        {'name': 'Transfermarkt', 'url': 'https://www.transfermarkt.ch'},
        {'name': 'UEFA Stats', 'url': 'https://www.uefa.com/uefachampionsleague/statistics/'},
    ],
    'NFL': [
        {'name': 'Pro-Football-Reference', 'url': 'https://www.pro-football-reference.com'},
        {'name': 'StatMuse', 'url': 'https://www.statmuse.com/nfl'},
        {'name': 'ESPN NFL', 'url': 'https://www.espn.com/nfl'},
    ],
    'NBA': [
        {'name': 'Basketball-Reference', 'url': 'https://www.basketball-reference.com'},
        {'name': 'StatMuse', 'url': 'https://www.statmuse.com/nba'},
        {'name': 'NBA Stats', 'url': 'https://www.nba.com/stats'},
    ],
    'NHL': [
        {'name': 'Hockey-Reference', 'url': 'https://www.hockey-reference.com'},
        {'name': 'NHL Stats', 'url': 'https://www.nhl.com/stats'},
        {'name': 'Natural Stat Trick', 'url': 'https://www.naturalstatrick.com'},
    ],
    'MLB': [
        {'name': 'Baseball-Reference', 'url': 'https://www.baseball-reference.com'},
        {'name': 'FanGraphs', 'url': 'https://www.fangraphs.com'},
        {'name': 'StatMuse', 'url': 'https://www.statmuse.com/mlb'},
    ],
    'F1': [
        {'name': 'Racing-Statistics', 'url': 'https://www.racing-statistics.com'},
        {'name': 'StatsF1', 'url': 'https://www.statsf1.com'},
        {'name': 'F1.com Stats', 'url': 'https://www.formula1.com/en/stats.html'},
    ],
    'Tennis': [
        {'name': 'Tennis Abstract', 'url': 'https://tennisabstract.com'},
        {'name': 'UltimateTennis', 'url': 'https://www.ultimatetennis.com'},
        {'name': 'TennisExplorer', 'url': 'https://www.tennisexplorer.com'},
    ],
    'Cycling': [
        {'name': 'ProCyclingStats', 'url': 'https://www.procyclingstats.com'},
        {'name': 'CyclingAnalytics', 'url': 'https://cyclinganalytics.com'},
        {'name': 'Cyclingnews', 'url': 'https://www.cyclingnews.com'},
    ],
    'Golf': [
        {'name': 'DataGolf', 'url': 'https://www.datagolf.com'},
        {'name': 'PGATour', 'url': 'https://www.pgatour.com/stats'},
        {'name': 'LPGA Stats', 'url': 'https://www.lpga.com/stats'},
    ],
    'Snooker': [
        {'name': 'SnookerBase', 'url': 'https://www.snooker.org'},
        {'name': 'Snookerfreak', 'url': 'https://www.snookerfreak.com'},
        {'name': 'Crucible Online', 'url': 'https://www.crucible-online.com'},
    ],
    'Darts': [
        {'name': 'DartsDatabase', 'url': 'https://www.dartsdatabase.co.uk'},
        {'name': 'StatBunker', 'url': 'https://www.statbunker.com'},
        {'name': 'PDC Stats', 'url': 'https://www.pdc.tv/stats'},
    ],
    'WRC': [
        {'name': 'eWRC Results', 'url': 'https://www.ewrc-results.com'},
        {'name': 'RallySport', 'url': 'https://www.rallysportmedia.com'},
        {'name': 'WRC.com', 'url': 'https://www.wrc.com'},
    ],
    'IIHF': [
        {'name': 'IIHF Stats', 'url': 'https://www.iihf.com/en/statistics'},
        {'name': 'HockeyWorld', 'url': 'https://www.hockeyworld.com'},
    ],
    'Swiss Hockey': [
        {'name': 'Swiss Hockey News', 'url': 'https://www.srf.ch/sport/eishockey'},
        {'name': 'National League', 'url': 'https://www.nationalleague.ch'},
        {'name': 'Swiss Ice Hockey', 'url': 'https://www.swiss-icehockey.ch'},
    ],
    'Swiss Football': [
        {'name': 'Super League', 'url': 'https://www.sfl.ch'},
        {'name': 'Swiss Football TV', 'url': 'https://www.sftv.ch'},
        {'name': 'football.ch', 'url': 'https://www.football.ch'},
    ],
}

# ============================================================================
# STOPWORDS - extended with common UI/nav strings and German stopwords
# ============================================================================
STOPWORDS = {
    # English
    'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
    'from', 'as', 'is', 'was', 'are', 'were', 'been', 'be', 'have', 'has', 'had', 'do', 'does', 'did',
    'will', 'would', 'could', 'should', 'may', 'might', 'must', 'shall', 'can', 'need', 'dare',
    'these', 'those', 'this', 'that', 'it', 'its', 'they', 'their', 'them', 'we', 'our', 'you',
    'your', 'he', 'she', 'him', 'her', 'his', 'hers', 'us', 'who', 'what', 'which',
    'when', 'where', 'why', 'how', 'all', 'each', 'every', 'both', 'few', 'more', 'most',
    'some', 'any', 'no', 'not', 'only', 'same', 'so', 'than', 'too', 'very', 'just',
    'now', 'here', 'there', 'then', 'first', 'new', 'old', 'high', 'small', 'big', 'large',
    'long', 'short', 'great', 'little', 'own', 'other', 'such', 'says', 'said', 'after',
    'before', 'over', 'under', 'again', 'once', 'says', 'according', 'report', 'reports',
    'million', 'billion', 'percent', 'year', 'years', 'day', 'days', 'time', 'times',
    'news', 'latest', 'today', 'breaking', 'world', 'update', 'updates', 'video', 'videos',
    'live', 'watch', 'read', 'more', 'home', 'page', 'site', 'search',
    # German
    'nicht', 'eine', 'einer', 'eines', 'einen', 'einem', 'auch', 'sich', 'sind', 'wird',
    'wurde', 'haben', 'hatte', 'sein', 'beim', 'beim', 'nach', 'noch', 'oder', 'wenn',
    'dass', 'wird', 'kann', 'aber', 'mehr', 'über', 'unter', 'gegen', 'jetzt', 'dann',
    'beim', 'durch', 'immer', 'schon', 'damit', 'dabei', 'doch', 'ohne', 'weil', 'plus',
    'dazu', 'hier', 'dort', 'dieser', 'diese', 'dieses', 'diesen', 'diesem', 'keine',
    'keiner', 'keinen', 'keinem', 'wurde', 'wurden', 'wird', 'werden', 'kann', 'könnte',
    'hätte', 'wäre', 'ihrer', 'ihren', 'ihrem', 'ihres', 'seine', 'seiner', 'seinen',
    'seinem', 'seines', 'sowie', 'damit', 'dabei', 'daran', 'darauf', 'dafür',
    'schweiz', 'schweizer', 'swiss', 'aktuell', 'aktuelle',
    # French
    'dans', 'avec', 'pour', 'mais', 'tout', 'plus', 'aussi', 'comme', 'cette',
    'sont', 'elle', 'nous', 'vous', 'leur', 'leurs', 'être', 'avoir',
}

# ============================================================================
# NEW: Article quality filter — removes website titles / navigation strings
# ============================================================================
JUNK_PATTERNS = [
    # Website titles (contain site name + tagline)
    r'breaking news.*video',
    r'latest news.*headlines',
    r'actualit[eé]s.*informations',
    r'aktuelle.*nachrichten',
    r'^news\s*\|',
    r'\|\s*today.*headlines',
    r'stay up to date with notifications',
    r'^opinions?\s*(&|&amp;|und|et)\s*chroniques?$',
    r'^actualit[eé]\s*des\s*r[eé]gions',
    r'^le choix de la r[eé]daction',
    r'^news home$',
    r'your daily (briefing|news)',
    r'^(home|search|menu|navigation|subscribe|sign in|log in)$',
    # Generic nav/menu items
    r'^(sport|news|politics|business|technology|culture|lifestyle)(\s+home)?$',
]

def is_real_article(title):
    """Returns True if this looks like a real article headline, not a site title or nav item."""
    t = title.strip().lower()
    # Too short
    if len(t) < 25:
        return False
    # Matches junk patterns
    for pattern in JUNK_PATTERNS:
        if re.search(pattern, t, re.IGNORECASE):
            return False
    # Contains a verb — real headlines almost always do
    # (very basic check: if it has a word boundary common in headlines)
    # Allow if it has at least one non-stopword word of 4+ chars
    words = re.findall(r'\b\w{4,}\b', t)
    real_words = [w for w in words if w not in STOPWORDS]
    return len(real_words) >= 3


def run_cron_mode(output_dir):
    os.makedirs(output_dir, exist_ok=True)
    print(f"Running cron mode - output to {output_dir}")
    print("Fetching world news...")
    world_data = fetch_world_news()
    with open(os.path.join(output_dir, 'news.json'), 'w') as f:
        json.dump(world_data, f)
    print(f"World news saved: {len(world_data.get('mustRead', []))} must-read articles")
    print("Fetching sports news...")
    sports_data = fetch_sports_news()
    with open(os.path.join(output_dir, 'sports.json'), 'w') as f:
        json.dump(sports_data, f)
    print(f"Sports saved: {len(sports_data.get('mustWatch', []))} must-watch articles")
    print("Cron job completed successfully")

def fetch_world_news():
    all_headlines = []
    source_results = {'swiss': [], 'world': []}
    for region, sources in WORLD_SOURCES.items():
        for source in sources:
            try:
                req = urllib.request.Request(
                    source['url'],
                    headers={
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                        'Accept': 'text/html,application/xhtml+xml',
                    }
                )
                with urllib.request.urlopen(req, timeout=10) as response:
                    html = response.read().decode('utf-8', errors='ignore')
                headlines = extract_headlines(html, source['url'])
                all_headlines.extend(headlines)
                avg_score = sum(h['sentiment'] for h in headlines) // len(headlines) if headlines else 50
                level, icon, color, label = get_sentiment_level(avg_score)
                source_results[region].append({
                    'name': source['name'],
                    'url': source['url'],
                    'headlineCount': len(headlines),
                    'sentiment': avg_score,
                    'level': level,
                    'icon': icon,
                    'color': color,
                    'label': label,
                    'headlines': headlines[:5]
                })
            except Exception as e:
                source_results[region].append({
                    'name': source['name'],
                    'url': source['url'],
                    'error': str(e)
                })
    all_titles = [h['title'] for h in all_headlines]
    all_text = ' '.join(all_titles)
    global_score = analyze_sentiment_score(all_text)
    global_level, global_icon, global_color, global_label = get_sentiment_level(global_score)
    trending = get_trending_topics(all_headlines)

    # Filter: only real articles with a URL for breaking + must-read
    real_headlines = [h for h in all_headlines if h.get('url') and is_real_article(h['title'])]
    breaking = [h for h in real_headlines if h['breaking']][:10]
    must_read = sorted(real_headlines, key=lambda x: abs(x['sentiment'] - 50), reverse=True)[:10]

    return {
        'type': 'world',
        'global': {
            'sentiment': global_score,
            'level': global_level,
            'icon': global_icon,
            'color': global_color,
            'label': global_label
        },
        'sources': source_results,
        'trending': trending,
        'breaking': breaking,
        'mustRead': must_read
    }

def fetch_sports_news():
    all_headlines = []
    source_results = {'swiss': [], 'global': []}
    for region, sources in SPORTS_SOURCES.items():
        for source in sources:
            try:
                req = urllib.request.Request(
                    source['url'],
                    headers={
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                        'Accept': 'text/html,application/xhtml+xml',
                    }
                )
                with urllib.request.urlopen(req, timeout=10) as response:
                    html = response.read().decode('utf-8', errors='ignore')
                headlines = extract_headlines(html, source['url'])
                all_headlines.extend(headlines)
                avg_heat = sum(h['heat'] for h in headlines) // len(headlines) if headlines else 0
                source_results[region].append({
                    'name': source['name'],
                    'url': source['url'],
                    'headlineCount': len(headlines),
                    'heat': avg_heat,
                    'headlines': headlines[:5]
                })
            except Exception as e:
                source_results[region].append({
                    'name': source['name'],
                    'url': source['url'],
                    'error': str(e)
                })
    total_heat_raw = sum(h['heat'] for h in all_headlines) if all_headlines else 0
    global_heat = min(100, int(math.log(total_heat_raw + 1) * 12))
    if global_heat <= 20:
        heat_level, heat_icon, heat_color, heat_label = 'iceberg', '🔵', '#06b6d4', 'ICEBERG'
    elif global_heat <= 40:
        heat_level, heat_icon, heat_color, heat_label = 'chill', '🟢', '#22c55e', 'CHILL'
    elif global_heat <= 60:
        heat_level, heat_icon, heat_color, heat_label = 'warming', '🟡', '#eab308', 'WARMING UP'
    elif global_heat <= 80:
        heat_level, heat_icon, heat_color, heat_label = 'hot', '🟠', '#f97316', 'HOT'
    else:
        heat_level, heat_icon, heat_color, heat_label = 'inferno', '🔥', '#ef4444', 'ON FIRE'

    # Filter: only real articles with URL for hot events and must-watch
    real_headlines = [h for h in all_headlines if h.get('url') and is_real_article(h['title'])]
    hot_events = sorted([h for h in real_headlines if h['heat'] > 0], key=lambda x: x['heat'], reverse=True)[:10]
    must_watch = sorted(real_headlines, key=lambda x: x['heat'], reverse=True)[:10]

    return {
        'type': 'sports',
        'global': {
            'heat': global_heat,
            'level': heat_level,
            'icon': heat_icon,
            'color': heat_color,
            'label': heat_label
        },
        'sources': source_results,
        'statsSites': STATS_SITES,
        'hotEvents': hot_events,
        'mustWatch': must_watch
    }

def analyze_sentiment_score(text):
    text_lower = text.lower()
    words = re.findall(r'\b\w+\b', text_lower)
    pos_count = sum(1 for w in words if w in POSITIVE_WORDS)
    neg_count = sum(1 for w in words if w in NEGATIVE_WORDS)
    total = pos_count + neg_count
    if total == 0:
        return 50
    ratio = (pos_count / (pos_count + neg_count)) * 100
    return int(ratio)

def get_sentiment_level(score):
    if score <= 16:
        return 'very_negative', '🔴🔴', '#f87171', 'Very Negative'
    elif score <= 33:
        return 'negative', '🔴', '#f87171', 'Negative'
    elif score <= 49:
        return 'slightly_negative', '🟡', '#fbbf24', 'Slightly Negative'
    elif score <= 66:
        return 'slightly_positive', '🟢', '#4ade80', 'Slightly Positive'
    elif score <= 82:
        return 'positive', '🟢🟢', '#4ade80', 'Positive'
    else:
        return 'very_positive', '🟢🟢', '#4ade80', 'Very Positive'

def is_breaking(text):
    text_lower = text.lower()
    return any(kw in text_lower for kw in BREAKING_KEYWORDS)

def calculate_heat_score(text):
    text_lower = text.lower()
    matched_keywords = []
    heat_score = 0
    detected_sports = []
    for kw in HIGH_HEAT_KEYWORDS:
        if kw in text_lower:
            heat_score += 5
            matched_keywords.append(kw)
    sport_weight = 1.0
    for sport, weight in SPORT_WEIGHTS.items():
        if sport in text_lower:
            if weight > sport_weight:
                sport_weight = weight
                if sport not in detected_sports:
                    detected_sports.append(sport)
    event_weight = 1.0
    for event, weight in EVENT_TYPE_WEIGHTS.items():
        if event in text_lower:
            if weight > event_weight:
                event_weight = weight
    sport_pos_count = sum(1 for w in text_lower.split() if w in SPORTS_POSITIVE)
    sport_neg_count = sum(1 for w in text_lower.split() if w in SPORTS_NEGATIVE)
    if sport_pos_count > 0 or sport_neg_count > 0:
        heat_score += (sport_pos_count * 8) - (sport_neg_count * 8)
        if sport_pos_count > sport_neg_count and sport_pos_count > 1:
            matched_keywords.append('positive_news')
        elif sport_neg_count > sport_pos_count and sport_neg_count > 1:
            matched_keywords.append('negative_news')
    final_score = heat_score * sport_weight * event_weight
    return min(100, int(final_score)), matched_keywords, detected_sports, sport_weight

def extract_headlines(html, source_url):
    from urllib.parse import urljoin
    parser = HeadlineParser()
    try:
        parser.feed(html)
    except:
        pass

    base_url = source_url
    headlines = []
    for i, title in enumerate(parser.titles[:15]):
        if len(title) > 20:
            url = parser.urls[i] if i < len(parser.urls) and parser.urls[i] else ''
            if url and not url.startswith('http'):
                url = urljoin(base_url, url)
            score = analyze_sentiment_score(title)
            heat, heat_kw, detected_sports, sport_weight = calculate_heat_score(title)
            headlines.append({
                'title': title[:200],
                'url': url,
                'sentiment': score,
                'breaking': is_breaking(title),
                'heat': heat,
                'heatKeywords': heat_kw,
                'detectedSports': detected_sports,
                'sportWeight': sport_weight
            })
    return headlines

def get_trending_topics(all_headlines):
    word_freq = {}
    # Only count words from real articles
    real = [h for h in all_headlines if h.get('url') and is_real_article(h['title'])]
    for hl in real:
        words = re.findall(r'\b\w{5,}\b', hl['title'].lower())  # min 5 chars to cut generic words
        for w in words:
            if w not in STOPWORDS and w not in POSITIVE_WORDS and w not in NEGATIVE_WORDS:
                word_freq[w] = word_freq.get(w, 0) + 1
    # Only include words that appear at least twice
    trending = [(w, c) for w, c in word_freq.items() if c >= 2]
    trending = sorted(trending, key=lambda x: x[1], reverse=True)[:15]
    return [t[0] for t in trending]

class HeadlineParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.titles = []
        self.urls = []
        self.current_url = None
        self.in_title = False
        self.in_headline = False
        self.current_tag = None
        self.in_article = False
        self.in_h1 = False

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        if tag in ['title', 'h1', 'h2']:
            self.in_title = True
            self.current_tag = tag
        elif tag == 'a':
            href = attrs_dict.get('href', '')
            if href and (href.startswith('http') or href.startswith('/')):
                self.current_url = href if href.startswith('http') else href
        elif tag in ['article', 'li'] and attrs_dict.get('class', ''):
            if 'headline' in attrs_dict['class'].lower() or 'story' in attrs_dict['class'].lower():
                self.in_headline = True

    def handle_endtag(self, tag):
        if tag in ['title', 'h1', 'h2']:
            self.in_title = False
            self.current_url = None
        if tag == 'article':
            self.in_headline = False
        if tag == 'a' and self.in_title:
            pass

    def handle_data(self, data):
        if self.in_title and data.strip() and len(data.strip()) > 15:
            title = data.strip()
            if title not in self.titles:
                self.titles.append(title)
                self.urls.append(self.current_url)

class FetchHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        static_dir = os.path.join(BASE_DIR, 'static')

        if self.path == '/' or self.path == '/index.html':
            self.serve_file(os.path.join(static_dir, 'index.html'))
            return
        if self.path == '/world':
            self.serve_file(os.path.join(static_dir, 'modules/world/dashboard.html'))
            return
        if self.path == '/sports':
            self.serve_file(os.path.join(static_dir, 'modules/sports/dashboard.html'))
            return
        if self.path == '/dashboard':
            self.serve_file(os.path.join(static_dir, 'modules/world/dashboard.html'))
            return
        if self.path == '/api/news':
            self.handle_world_news()
            return
        if self.path == '/api/sports':
            self.handle_sports_news()
            return

        # Serve static files (CSS, JS, etc.)
        if self.path.startswith('/'):
            file_path = os.path.join(static_dir, self.path.lstrip('/'))
            if os.path.isfile(file_path):
                self.serve_file(file_path)
                return

        self.send_error(404, 'Not found')

    def serve_file(self, filepath):
        if os.path.exists(filepath):
            ext = os.path.splitext(filepath)[1]
            content_types = {
                '.html': 'text/html; charset=utf-8',
                '.css': 'text/css; charset=utf-8',
                '.js': 'application/javascript; charset=utf-8',
                '.json': 'application/json',
                '.ico': 'image/x-icon',
                '.png': 'image/png',
                '.jpg': 'image/jpeg',
            }
            ct = content_types.get(ext, 'text/html; charset=utf-8')
            with open(filepath, 'rb') as f:
                self.send_response(200)
                self.send_header('Content-type', ct)
                self.end_headers()
                self.wfile.write(f.read())
        else:
            self.send_error(404, 'File not found')

    def handle_world_news(self):
        data = fetch_world_news()
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def handle_sports_news(self):
        data = fetch_sports_news()
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def log_message(self, format, *args):
        pass

class ReusableTCPServer(socketserver.TCPServer):
    allow_reuse_address = True

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='News Dashboard Server')
    parser.add_argument('--cron', action='store_true', help='Run in cron mode: fetch news and save JSON, then exit')
    parser.add_argument('--output-dir', type=str, default=None, help='Directory to save JSON files (for cron mode)')
    args = parser.parse_args()

    if args.cron:
        if not args.output_dir:
            print("Error: --output-dir is required when using --cron")
            exit(1)
        run_cron_mode(args.output_dir)
    else:
        print(f"News Dashboard running at http://localhost:{PORT}")
        print(f"Start Page:  http://localhost:{PORT}/")
        print(f"World News:  http://localhost:{PORT}/world")
        print(f"Sports:      http://localhost:{PORT}/sports")
        try:
            with ReusableTCPServer(('0.0.0.0', PORT), FetchHandler) as httpd:
                httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")
        except Exception as e:
            print(f"Server error: {e}")
