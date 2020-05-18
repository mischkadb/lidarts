$(document).ready(function() {
    var tournament_hashid = $('#tournament_hashid').data()['hashid'];

    function shuffle(array) {
        var currentIndex = array.length, temporaryValue, randomIndex;
      
        // While there remain elements to shuffle...
        while (0 !== currentIndex) {
      
          // Pick a remaining element...
          randomIndex = Math.floor(Math.random() * currentIndex);
          currentIndex -= 1;
      
          // And swap it with the current element.
          temporaryValue = array[currentIndex];
          array[currentIndex] = array[randomIndex];
          array[randomIndex] = temporaryValue;
        }
      
        return array;
      }

    sortable = new Sortable(
        playerList, 
        { 
            animation: 100,
            group: 'list-1',
            draggable: '.list-group-item',
            handle: '.list-group-item',
            sort: true,
            filter: '.sortable-disabled',
            onEnd: function (/**Event*/evt) {
                $('.playerListNumber').each(function (i) {
                    var numbering = i + 1;
                    $(this).text(numbering);
                });
                $('#player_list').val(sortable.toArray());
            },
        }
    ); 
    $('#player_list').val(sortable.toArray());

    $('#shuffleSeedsButton').click( function () {
        num_seeds = $('#numberOfSeeds').val();
        sortable_array = sortable.toArray();
        sortable_without_seeds = sortable_array.slice(num_seeds);
        shuffle(sortable_without_seeds);

        sortable.sort(sortable_array.slice(0, 2).concat(sortable_without_seeds));
        $('.playerListNumber').each(function (i) {
            var numbering = i + 1;
            $(this).text(numbering);
        });
        $('#player_list').val(sortable.toArray());
    });

    $('.apply-button').click( function (event) {
        event.preventDefault();
        this_round = this.id.replace('applyToAll-', '');
        type_ = $('#' + this_round + '-type_').val();
        bo_sets = $('#' + this_round + '-bo_sets').val();
        bo_legs = $('#' + this_round + '-bo_legs').val();
        two_clear_legs = $('#' + this_round + '-two_clear_legs').prop("checked");
        console.log(two_clear_legs);
        in_mode = $('#' + this_round + '-in_mode').val();
        out_mode = $('#' + this_round + '-out_mode').val();
        starter = $('#' + this_round + '-starter').val();
        score_input_delay = $('#' + this_round + '-score_input_delay').val();

        for (i=0; i < 10; i++) {
            $('#rounds-' + i + '-type_').val(type_);
            $('#rounds-' + i + '-bo_sets').val(bo_sets);
            $('#rounds-' + i + '-bo_legs').val(bo_legs);
            $('#rounds-' + i + '-two_clear_legs').prop("checked", two_clear_legs);
            $('#rounds-' + i + '-in_mode').val(in_mode);
            $('#rounds-' + i + '-out_mode').val(out_mode);
            $('#rounds-' + i + '-starter').val(starter);
            $('#rounds-' + i + '-score_input_delay').val(score_input_delay);
        }
    });

});
