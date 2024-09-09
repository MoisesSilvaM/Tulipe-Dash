window.dashExtensions = Object.assign({}, window.dashExtensions, {
    default: {
        function0: function(feature, context) {
            const {
                selected
            } = context.hideout;
            if (selected.includes(feature.properties.id)) {
                return {
                    fillColor: '#b2b2b2',
                    color: '#b2b2b2'
                }
            }
            return {
                fillColor: '#1a73e8',
                color: '#1a73e8'
            }
        },
        function1: function(feature, context) {
                const {
                    colorscale,
                    classes,
                    colorProp,
                    closed
                } = context.hideout;
                const value = feature.properties[colorProp];

                let fillColor;
                for (let i = 0; i < classes.length; ++i) {
                    if (value > classes[i]) {
                        fillColor = colorscale[i]; // set the fill color according to the class
                    }
                }
                if (closed.includes(feature.properties.id)) {
                    return {
                        fillColor: '#a8a8a8',
                        color: '#a8a8a8'
                    }
                }
                return {
                    fillColor: fillColor,
                    color: fillColor
                };
            }

            ,
        function2: function(feature, layer, context) {
            layer.bindTooltip(`${feature.properties.name} (id:${feature.properties.id})`)
        },
        function3: function(feature, layer, context) {
            const {
                colorProp,
                tname,
                closed
            } = context.hideout;
            if (closed.includes(feature.properties.id)) {
                layer.bindTooltip(`${feature.properties.name} (Closed street)`)
            } else {
                layer.bindTooltip(`${feature.properties.name} (${tname}: ${feature.properties[colorProp].toFixed()})`)
            }
        }
    }
});