# -*- coding: utf-8 -*-

"""Routes for legal stuff.

Includes disclaimer, privacy notice, imprint, T&C etc.
"""

from flask import render_template

from lidarts.legal import bp


@bp.route('/legal_notice')
def legal_notice():
    """Legal notice (English).

    Returns:
        Legal notice template
    """
    return render_template('legal/legal_notice.html')


@bp.route('/disclaimer')
def disclaimer():
    """Disclaimer (English).

    Returns:
        Disclaimer template
    """
    return render_template('legal/disclaimer.html')


@bp.route('/privacy')
def privacy():
    """Privacy notice (English).

    Returns:
        Privacy template
    """
    return render_template('legal/privacy.html')


@bp.route('/legal_notice/german')
def legal_notice_german():
    """Legal notice (German).

    Returns:
        Legal notice template
    """
    return render_template('legal/german/legal_notice.html')


@bp.route('/disclaimer/german')
def disclaimer_german():
    """Disclaimer (German).

    Returns:
        Disclaimer template
    """
    return render_template('legal/german/disclaimer.html')


@bp.route('/privacy/german')
def privacy_german():
    """Privacy notice (German).

    Returns:
        Privacy template
    """
    return render_template('legal/german/privacy.html')


@bp.route('/terms_and_conditions')
def terms_and_conditions():
    """Terms and Conditions (English).

    Returns:
        T&C template
    """
    return render_template('legal/terms_and_conditions.html')
