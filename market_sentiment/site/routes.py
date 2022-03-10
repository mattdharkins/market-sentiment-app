from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required



from market_sentiment.models import *

site = Blueprint('site', __name__, template_folder = 'site_templates')

"""
Note that in the above code some arguments are specified the Blueprint object.
The first argument, 'site' is the Blueprint's name, which is used by
Flask's routing mechanism. The second argument, __name__, is the Blueprint's
import name, which Flask uses to locate the Blueprint's resources.

"""

@site.route('/')
def home():
    return render_template('index.html')

@site.route('/methodology')
def methodology():
    return render_template('methodology.html')

@site.route('/market-sentiment')
@login_required
def market_sentiment():
    args = request.args.to_dict()

    if 'quoteDate' in args:
        ois = OptionsInfo.query.filter_by(quoteDate = args['quoteDate'])
        bullish_count = 0
        bearish_count = 0
        neutral_count = 0
        total_count = 0
        for oi in ois:
            total_count+=1
            if oi.sentiment == "Bullish":
                bullish_count+=1
            elif oi.sentiment == "Bearish":
                bearish_count+=1
            else:
                neutral_count+=1
        overall_sentiment = None
        if bullish_count >= 0.6 * total_count:
            overall_sentiment = "Bullish"
        elif bearish_count >= 0.6 * total_count:
            overall_sentiment = "Bearish"
        else:
            overall_sentiment = "Neutral"

        return render_template('market-sentiment.html', optionsInfos=ois, qDate=args['quoteDate'], overallSentiment = overall_sentiment)
    else:
        return render_template('market-sentiment.html')