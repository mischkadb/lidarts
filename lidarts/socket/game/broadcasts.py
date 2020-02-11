def broadcast_game_aborted(game):
    emit('game_aborted', {'hashid': game.hashid}, room=game.hashid, namespace='/game', broadcast=True)



def broadcast_new_game(game):
    p1_name, = User.query.with_entities(User.username).filter_by(id=game.player1).first_or_404()
    p2_name, = User.query.with_entities(User.username).filter_by(id=game.player2).first_or_404()

    emit('send_system_message_new_game', {'hashid': game.hashid, 'p1_name': p1_name, 'p2_name': p2_name},
         broadcast=True, namespace='/chat')


def broadcast_game_completed(game):
    p1_name, = User.query.with_entities(User.username).filter_by(id=game.player1).first_or_404()
    p2_name, = User.query.with_entities(User.username).filter_by(id=game.player2).first_or_404()

    if game.bo_sets > 1:
        p1_score = game.p1_sets
        p2_score = game.p2_sets
    else:
        p1_score = game.p1_legs
        p2_score = game.p2_legs

    emit('send_system_message_game_completed', {'hashid': game.hashid, 'p1_name': p1_name, 'p2_name': p2_name,
                                                'p1_score': p1_score, 'p2_score': p2_score},
         broadcast=True, namespace='/chat')