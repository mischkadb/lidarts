from flask import render_template
from lidarts.legal import bp


@bp.route('/legal_notice')
def legal_notice():
    return render_template('legal/legal_notice.html')


@bp.route('/disclaimer')
def disclaimer():
    return render_template('legal/disclaimer.html')


@bp.route('/privacy')
def privacy():
    return render_template('legal/privacy.html')


@bp.route('/legal_notice/german')
def legal_notice_german():
    return render_template('legal/german/legal_notice.html')


@bp.route('/disclaimer/german')
def disclaimer_german():
    return render_template('legal/german/disclaimer.html')


@bp.route('/privacy/german')
def privacy_german():
    return render_template('legal/german/privacy.html')


@bp.route('/terms_and_conditions')
def terms_and_conditions():
    return render_template('legal/terms_and_conditions.html')
