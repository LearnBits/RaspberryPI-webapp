/*! AntColorPicker V1.12
 * Copyright (c) 2015 AntProduction
 * http://antproduction.free.fr/AntColorPicker
 * https://github.com/antrax2013/AntColorPicker
 *
 * GPL license:
 *   http://www.gnu.org/licenses/gpl.html
 *
 * Contributor: antrax2013@hotmail.com
 *
 */

;(function ($) {
    $.fn.AntColorPicker = function(options) {

        //definition de la strucutre Html de base de la palette
        var contentTemplate = '<div id="AntColorPicker" class="AntColorPicker">';
        contentTemplate += '<ul>';
        contentTemplate += "#contentLineTemplate#";
        contentTemplate += '</ul>';
        contentTemplate += '#crossToClose#';
        contentTemplate += '</div>';

        var contentLineTemplate = '<li><a name="#color#" rel="#color#" style="background:#color#;" title="#color#"></a></li>';

        var templateCorssToClose = '<a id="CloseColorPicker" class="AntColorPickerClose" title="#labelClose#">#labelClose#</a>';

        //Méthode privée remplaçant les tags
        function TagConvertor(chaine, TagList, joker) {

            var _mask = (joker == undefined)? "#":joker;

            for (var val in TagList) chaine = chaine.replace(new RegExp(_mask+val+_mask, "g"), TagList[val]);

            return chaine;
        }

        //Méthode privée alimentant le template
        function contentBuilder(contentLine) {
            var content='';
            var color='';
            var values = ['00', '33', '66', '99', 'CC', 'FF'];
            for (r = 0; r < 6; r++) {
                for (g = 0; g < 6; g++) {
                    for (b = 0; b < 6; b++) {
                        color = '#' + values[r] + values[g] + values[b];
                        content += TagConvertor(contentLine,{"color":color});
                    }
                }
            }
            return content;
        }

        //On définit nos paramètres par défaut
        var defauts=
        {
            builder: function(contentTempLinelate, contentTemplate, templateCorssToClose, labelClose) { //méthode construisant la palette
                var content = contentBuilder(contentTempLinelate);
                content = contentTemplate.replace("#contentLineTemplate#",content);
                return content;
            },
            __callback: null, // added by DK
            contentLineTemplate: contentLineTemplate,
            contentTemplate: contentTemplate,
            iconPath: "../public/images/antColorPicker/",
            labelClose:"Fermer",
            labelRAZColor:"Réinitialiser la valeur",
            largeurPalette: 390,
            withRAZOption: true,
            withCrossToClose: true,
            withPaletteIcon: true,
            zIndex: 1500,
            $BGColorTarget:'#AntColorPicker'
        };

        //Lecture des paramétres et fusion avec ceux par défaut
        var parametres=$.extend(true, defauts, options);

        return this.each(function () {

            var $$ = $(this);
            var oldVal = "";
            var saisie=false;

            if(parametres.withPaletteIcon) $$.addClass("AntColorPickerIconeInput");

            //Mise en palce de la couleur de fond en fonction de la valeur du champ
            $$.attr("style", "background-color:" + $$.val());

            /** DK: I removed the RAZ button
            //Ajout du bouton RAZ
            var id = "RaZAntColorPicker_" + Math.floor(Math.random() * 10000);
            var content = (parametres.withRAZOption == false)? '' : ' <img id="' + id + '" title="'+parametres.labelRAZColor+'" style="height:'+$$.css("height")+'" class="RaZAntColorPicker" src="'+parametres.iconPath+'vide.png" />';
            $(content).insertAfter($$);


            //if(parametres.withIconeInInput) $$.addClass('AntColorPickerIconeInput');
                //$$.css('background', "url('"+parametres.iconPath+"palette.png') no-repeat right");

            $('#' + id).bind("click", function () {
                $$.val("");
                $$.attr("style", "background-color:" + "");
            });
            */

            // Récupération des coordonnées pour placer la palette
            var x; //= $$.offset().left;
            var y; //= $$.offset().top + $$.outerHeight(true);
            var largeurEcran = $(document).width();

            // Lorsque le curseur entre dans le champ de saisi
            $$.focusin(function (e) { start(e); });

            // Lorsque l'on click sur le champ de saisie
            $$.click(function (e) { start(e); });

            function start(e) {
                oldVal = $$.val();
                saisie=false;
                x = $$.offset().left;

                if ((x + parametres.largeurPalette) > largeurEcran) x -= parametres.largeurPalette;

                y = $$.offset().top + $$.outerHeight(true);
                e.stopImmediatePropagation();
                $(document).one('click', removeColorPicker);
                buildColorPicker();
            };

            $$.focusout(function () {
                var tmp = $$.val();
                var reg1 = new RegExp("^[#]?[0-9A-Fa-f]{3}([0-9A-Fa-f]{3})?$", "g");

                if (tmp.indexOf("#") == -1 && tmp != "") $$.val("#" + $$.val());
                if (!tmp.match(reg1)) $$.val(oldVal);
                else {
                    //si on a pas saisie dans l'input, il ne faut pas retirer le color picker sinon on coupe l'herbe sous le pied du click
                    if(saisie){
                        $$.css('backgroundColor', $$.val());
                        chooseFontColor();
                        removeColorPicker();
                    }
                }
            });

            // Fonction mettant une couleur de font claire quand la couleur choisie est foncée et vis versa
            function chooseFontColor() {
                var input = $$.val().replace("#","").toLowerCase();

                var black = false;
                var tmp=""

                for(i=0; i< 6; i+=2) {
                    tmp+=" "+input.substr(i,2).toString()
                    black |= parseInt(input.substr(i,2),16) > 128;
                }

                if(!black) $$.addClass('AntColorPicker-whiteFont');
                else $$.removeClass('AntColorPicker-whiteFont');
            }


            // Fonction de création de la palette
            function buildColorPicker() {
                // On supprime d'éventuelles autres palettes déjà ouvertes
                removeColorPicker();

                // On construit le Html de la palette
                if (typeof (parametres.builder) == 'function') {
                    if(parametres.withCrossToClose!=true) {
                        parametres.contentTemplate = parametres.contentTemplate.replace("#crossToClose#","");
                    }
                    else {
                        parametres.contentTemplate = TagConvertor(parametres.contentTemplate,{ "crossToClose": templateCorssToClose, "labelClose":parametres.labelClose});
                    }

                    var content = parametres.builder(parametres.contentLineTemplate, parametres.contentTemplate);
                }
                else throw "Error: the builder parameter must be a function.";

                // On la place dans la page aux coordonnées du textfield
                $(content).css({
                    position: 'absolute',
                    left: x,
                    top: y,
                    zIndex: parametres.zIndex,
                    width: parametres.largeurPalette + 'px'
                }).appendTo('body'); // Insertion dans le body html

                //Affectation à la cible de la couleur courante
                $(parametres.$BGColorTarget).css('backgroundColor', $$.val());

                // Au survol d'une couleur, on change le fond de la palette
                $('#AntColorPicker a').hover(function () {
                    $(parametres.$BGColorTarget).css('backgroundColor', $(this).attr('rel')); // Si l'élément à déjà une couleur on l'utilise
                }, function () {
                    $(parametres.$BGColorTarget).css('backgroundColor', $$.val());
                });

                // DK : need to capture this event so and send a LED command to the shield
                // Lorsqu'une couleur est cliqué, on affiche la valeur dans le textfield (se fait après le focus out)
                $('#AntColorPicker a').not('.AntColorPickerClose .RaZAntColorPicker').click(function (event) {
                    var color_picked = $(this).attr('rel');
                    $$.val(color_picked);
                    $$.css('backgroundColor', color_picked);
                    chooseFontColor();
                    removeColorPicker();
                    // Added by DK
                    if(parametres.__callback)
                      parametres.__callback();
                });

                // Au survol d'une couleur, on change le fond
                $('#AntColorPicker a').mouseover(function () {
                    $(parametres.$BGColorTarget).css('backgroundColor', $(this).attr('rel'));
                });

                // On supprime la palette si le lien "Fermer" est cliqué
                $('#AntColorPicker a.close').click(function () {
                    removeColorPicker();
                });

                //Fermeture de la palette si on presse la touche escape
                $$.keyup(function( event ) {
                    if ( event.keyCode == 27 ) { removeColorPicker(); }
                    else saisie=true;
                });
            }

            // Fonction de suppression de la palette
            function removeColorPicker() {
                $('#AntColorPicker').remove();
            }
        });
    };
})(jQuery);
