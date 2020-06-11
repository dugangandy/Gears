(function ($) {
    var DemoIndex = {};
    DemoIndex.NodeType = {SOA: 1, DB: 2, Cache: 3};
    DemoIndex.NodeStatus = {
        Error: {value: 1, color: "#ED5565"},
        Warning: {value: 2, color: "#F8AC59"},
        Ok: {value: 3, color: "#1AB394"},
        Unknow: {value: -1, color: "#CCCCCC"}
    };
    DemoIndex.ShapeStyle = {
        Cycle: "shape=ellipse;perimeter=ellipsePerimeter",
        Rectangle: "shape=rectangle;perimeter=rectanglePerimeter",
        Diamond: "shape=rhombus;perimeter=rhombusPerimeter"
    };
    DemoIndex.IdGenerator = (function () {
        var count = 0;
        return {
            next: function () {
                count++;
                return count;
            }
        }
    })();

    DemoIndex.BaseNode = $.Base.Event.extend({
        init: function (pOpts) {
            this._NodeType = pOpts.NodeType;
            this._NodeStatus = null;
            this._NodeTitle = "";
            this._NodeMoreInfo = "";
            this._cor = {};

            this._vertext = null;
            this._id = DemoIndex.IdGenerator.next();
        },
        setCor: function (cor) {
            this._cor = cor;
        },
        getCor: function () {
            return this._cor;
        },
        setVertex: function (vertex) {
            this._vertext = vertex;
        },
        getVertex: function () {
            return this._vertext;
        },
        setNodeMoreInfo: function (moreInfo) {
            this._NodeMoreInfo = moreInfo;
        },
        setNodeTitle: function (title) {
            this._NodeTitle = title;
        },
        setNodeStatus: function (nodeStatus) {
            this._NodeStatus = nodeStatus;
        },
        getId: function () {
            return this._id;
        },
        getNodeTitle: function () {
            return this._NodeTitle;
        },
        getNodeMoreInfo: function () {
            return this._NodeMoreInfo;
        },
        getNodeStatus: function () {
            return this._NodeStatus;
        },
        getNodeType: function () {
            return this._NodeType;
        },
        calcLeftCor: function (context) {
            var a = (context.graphyTW - context.padding * 2 - context.cellW) / 2;

            return {
                x: a * (Math.cos(context.angle) + 1),
                y: a * (Math.sin(context.angle) + 1)
            };
        },
        getEdgeStyle: function () {
            var style = [];
            switch (this.getNodeStatus().value) {
                case DemoIndex.NodeStatus.Ok.value:
                    // style.push(mxConstants.STYLE_STROKECOLOR + "=" + DemoIndex.NodeStatus.Ok.color)
                    style.push(mxConstants.STYLE_FILLCOLOR + "=" + DemoIndex.NodeStatus.Ok.color);
                    break;
                case DemoIndex.NodeStatus.Warning.value:
                    // style.push(mxConstants.STYLE_STROKECOLOR + "=" + DemoIndex.NodeStatus.Warning.color)
                    style.push(mxConstants.STYLE_FILLCOLOR + "=" + DemoIndex.NodeStatus.Warning.color);
                    break;
                case DemoIndex.NodeStatus.Error.value:
                    style.push(mxConstants.STYLE_STROKECOLOR + "=" + DemoIndex.NodeStatus.Error.color);
                    style.push(mxConstants.STYLE_FILLCOLOR + "=" + DemoIndex.NodeStatus.Error.color);
                    break;
                case DemoIndex.NodeStatus.Unknow.value:
//                    style.push(mxConstants.STYLE_STROKECOLOR + "=" + DemoIndex.NodeStatus.Unknow.color);
                    style.push(mxConstants.STYLE_FILLCOLOR + "=" + DemoIndex.NodeStatus.Unknow.color);
                    break;
            }
            return style.join(";")
        },
        getNodeStyle: function () {
            var style = [];
            switch (this.getNodeStatus().value) {
                case DemoIndex.NodeStatus.Ok.value:
                    style.push(mxConstants.STYLE_STROKECOLOR + "=" + DemoIndex.NodeStatus.Ok.color);
                    style.push(mxConstants.STYLE_FILLCOLOR + "=" + DemoIndex.NodeStatus.Ok.color);
                    break;
                case DemoIndex.NodeStatus.Warning.value:
                    style.push(mxConstants.STYLE_STROKECOLOR + "=" + DemoIndex.NodeStatus.Warning.color);
                    style.push(mxConstants.STYLE_FILLCOLOR + "=" + DemoIndex.NodeStatus.Warning.color);
                    break;
                case DemoIndex.NodeStatus.Error.value:
                    style.push(mxConstants.STYLE_FONTCOLOR + "=white");
                    style.push(mxConstants.STYLE_STROKECOLOR + "=" + DemoIndex.NodeStatus.Error.color);
                    style.push(mxConstants.STYLE_FILLCOLOR + "=" + DemoIndex.NodeStatus.Error.color);
                    break;
                case DemoIndex.NodeStatus.Unknow.value:
                    style.push(mxConstants.STYLE_STROKECOLOR + "=" + DemoIndex.NodeStatus.Unknow.color);
                    style.push(mxConstants.STYLE_FILLCOLOR + "=" + DemoIndex.NodeStatus.Unknow.color);
                    break;
            }

            return style.join(";");
        }
    });

    DemoIndex.DBNode = DemoIndex.BaseNode.extend({
        init: function (pOpts) {
            this._super({NodeType: DemoIndex.NodeType.DB});

            this.drawShapeInfo = DemoIndex.ShapeStyle.Rectangle;
        },
        //context{graphyTW,padding,cellW,angle,parent,centerVertex}
        drawNode: function (graphy, context) {
            var self = this,
                cor = this.calcLeftCor(context);
            //console.log(cor);

            var style = this.getNodeStyle();
            style += ";" + this.drawShapeInfo;

            //console.log("style", style);

            var vertex = graphy.insertVertex(context.parent, null, this.getNodeTitle(), cor.x, cor.y, context.cellW, context.cellW, style);
            this.setCor(cor);
            //vertex.cor = cor;

            this.setVertex(vertex);
            return vertex;
        },
        //context{graphyTW,padding,cellW,angle,parent,centerVertex}
        drawEdge: function (graphy, context) {
            var self = this;

            var style = this.getEdgeStyle();

            var edge = graphy.insertEdge(context.parent, null, null, context.centerVertex, this.getVertex(), style);

            return edge;
        }

    });

    DemoIndex.CacheNode = DemoIndex.BaseNode.extend({
        init: function (pOpts) {
            this._super({NodeType: DemoIndex.NodeType.Cache});

            this.drawShapeInfo = DemoIndex.ShapeStyle.Diamond;
        },
        drawNode: function (graphy, context) {
            var self = this,
                cor = this.calcLeftCor(context);

            // console.log(cor);

            var style = this.getNodeStyle();
            style += ";" + this.drawShapeInfo;

            var vertex = graphy.insertVertex(context.parent, null, this.getNodeTitle(), cor.x, cor.y, context.cellW, context.cellW, style);
            this.setCor(cor);

            this.setVertex(vertex);
            return vertex;
        },
        //context{graphyTW,padding,cellW,angle,parent,centerVertex}
        drawEdge: function (graphy, context) {
            var self = this;

            var style = this.getEdgeStyle();

            var edge = graphy.insertEdge(context.parent, null, null, context.centerVertex, this.getVertex(), style);

            return edge;
        }
    });

    DemoIndex.SOANode = DemoIndex.BaseNode.extend({
        init: function (pOpts) {
            this._super({NodeType: DemoIndex.NodeType.SOA});

            this.drawShapeInfo = DemoIndex.ShapeStyle.Cycle;
        },
        drawNode: function (graphy, context) {
            var self = this,
                cor = this.calcLeftCor(context);

            //console.log(cor);

            var style = this.getNodeStyle();
            style += ";" + this.drawShapeInfo;

            var vertex = graphy.insertVertex(context.parent, null, this.getNodeTitle(), cor.x, cor.y, context.cellW, context.cellW, style);
            this.setCor(cor);

            this.setVertex(vertex);
            return vertex;
        },
        //context{graphyTW,padding,cellW,angle,parent,centerVertex}
        drawEdge: function (graphy, context) {
            var self = this;

            var style = this.getEdgeStyle();

            var edge = graphy.insertEdge(context.parent, null, null, context.centerVertex, this.getVertex(), style);

            return edge;
        }
    });

    DemoIndex.NodeFactory = {
        createNode: function (nodeType) {
            var node = null;
            switch (nodeType) {
                case DemoIndex.NodeType.SOA:
                    node = new DemoIndex.SOANode();
                    break;
                case DemoIndex.NodeType.Cache:
                    node = new DemoIndex.CacheNode();
                    break
                case DemoIndex.NodeType.DB:
                    node = new DemoIndex.DBNode();
                    break
            }

            return node;
        }
    }

    DemoIndex.Base = $.Base.Event.extend({
        init: function (pOpts) {
            $.extend(true, this, {
                $GraphyContainer: null,
                nodeData: {}
            }, pOpts);

            this.setOptions();
        },
        setOptions: function () {
            var self = this;

            this.graphy = new DemoIndex.Graphy({
                $container: self.$GraphyContainer,
                nodeData: self.nodeData,
                $base: self
            });

            this.graphy.addEvent("clickEdge", function (node) {
                var alert_icon = 'info';
                switch (node.getNodeStatus().value) {
                    case DemoIndex.NodeStatus.Ok.value:
                        alert_icon = 'info';
                        break;
                    case DemoIndex.NodeStatus.Warning.value:
                        alert_icon = 'warning';
                        break;
                    case DemoIndex.NodeStatus.Error.value:
                        alert_icon = 'error';
                        break;
                    case DemoIndex.NodeStatus.Unknow.value:
                        alert_icon = 'info';
                        break;
                }
                if (node.getNodeMoreInfo() != '') {
                    swal(node.getNodeTitle(), node.getNodeMoreInfo(), alert_icon);
                }

            })
        },
        destoryGraphy: function () {
            this.graphy._clearGraphy();
        }
    });

    //graphyTW,padding,cellW,angle,parent,centerVertex
    DemoIndex.Graphy = $.Base.Event.extend({
        init: function (pOpts) {

            $.extend(true, this, {
                $container: null,
                nodeData: {
                    nodes: null,
                    systemAlias: "",
                    graphyTW: 800,
                    cellW: 100,
                    padding: 20
                }
            }, pOpts);

            this.setOptions();

            this.render();
        },
        setOptions: function () {
            var self = this;

            this.graph = null;
            this.model = null;

            this.newEvent("clickEdge");

            this.drawNodeList = {};
            this.config = {
                padding: self.nodeData.padding,
                cellW: self.nodeData.cellW,
                graphyTW: self.nodeData.graphyTW
            };
            var a = this.config.graphyTW / 2 - this.config.padding;
            this.centerNodeCor = {
                x: a,
                y: a
            }

        },
        render: function (data) {
            var self = this;
            this._clearGraphy();

            if (!mxClient.isBrowserSupported()) {
                mxUtils.error('Browser is not supported!', 200, false);
            } else {
                this._initGraphyConfig();
                this._bindGraphEvent();
                this._draw();
            }
        },
        _draw: function () {
            var self = this;

            self.graph.getModel().beginUpdate();

            try {
                //create center of a cycle
                this._createCenterVertex();

                var e = Math.PI * 2 / this.nodeData.nodes.length;
                //create the other node
                $.each(this.nodeData.nodes, function (i, item) {
                    var angle = e * (i + 1);
                    var context = self._createContext(angle, self.parent, self.centerVertex);
                    var node = DemoIndex.NodeFactory.createNode(item.nodeType);
                    node.setNodeStatus(item.status);
                    node.setNodeMoreInfo(item.moreInfo);
                    node.setNodeTitle(item.title);

                    var vertex = node.drawNode(self.graph, context);
                    self.vertexs[vertex.id] = node;

                    var edge = node.drawEdge(self.graph, context);
                    self.edges.push(edge);
                })

                // var layout = new mxFastOrganicLayout(graph);
                // layout.execute(self.graph);
            } finally {
                self.graph.getModel().endUpdate();
            }

        },
        _createCenterVertex: function () {
            var self = this;

            this.centerVertex = this.graph.insertVertex(this.parent, null, this.nodeData.systemAlias, this.centerNodeCor.x - this.config.cellW / 2, this.centerNodeCor.y - this.config.cellW / 2, this.config.cellW, this.config.cellW, DemoIndex.ShapeStyle.Cycle)
            this.centerVertex.cor = this.centerNodeCor;

        },
        _createContext: function (angle, parent, centerVertex) {
            var self = this;
            return {
                padding: this.config.padding,
                cellW: this.config.cellW,
                graphyTW: this.config.graphyTW,
                angle: angle,
                parent: parent || null,
                centerVertex: centerVertex
            };
        },
        _initGraphyConfig: function () {
            var self = this;

            this.node = this.$container[0];
            this.model = new mxGraphModel();
            this.graph = new mxGraph(this.node, this.model);
            this.graph.setConnectable(true);
            this.edges = [];
            this.vertexs = {};

            // Creates the default style for vertices
            var style = [];
            style[mxConstants.STYLE_SHAPE] = mxConstants.SHAPE_RECTANGLE;
            style[mxConstants.STYLE_PERIMETER] = mxPerimeter.RectanglePerimeter;
            style[mxConstants.STYLE_STROKECOLOR] = 'gray';
            style[mxConstants.STYLE_ROUNDED] = true;
            style[mxConstants.STYLE_FILLCOLOR] = '#EEEEEE';
//            style[mxConstants.STYLE_GRADIENTCOLOR] = 'white';
            style[mxConstants.STYLE_FONTCOLOR] = '#774400';
            style[mxConstants.STYLE_ALIGN] = mxConstants.ALIGN_CENTER;
            style[mxConstants.STYLE_VERTICAL_ALIGN] = mxConstants.ALIGN_MIDDLE;
            style[mxConstants.STYLE_FONTSIZE] = '10';
            style[mxConstants.STYLE_FONTSTYLE] = 1;
            this.graph.getStylesheet().putDefaultVertexStyle(style);

            // Creates the default style for edges
            style = [];
            style[mxConstants.STYLE_SHAPE] = mxConstants.SHAPE_CONNECTOR;
            style[mxConstants.STYLE_STROKECOLOR] = '#6482B9';
            // style[mxConstants.VERTEX_SELECTION_STROKEWIDTH] = "20";
            // style[mxConstants.STYLE_ALIGN] = mxConstants.ALIGN_BOTTOM;
            // style[mxConstants.STYLE_VERTICAL_ALIGN] = mxConstants.ALIGN_LEFT;
            style[mxConstants.STYLE_EDGE] = mxEdgeStyle.SideToSide;
            style[mxConstants.STYLE_ENDARROW] = mxConstants.ARROW_OPEN;
            style[mxConstants.STYLE_FONTSIZE] = '12';
            style[mxConstants.STYLE_STROKEWIDTH] = '3';
            this.graph.getStylesheet().putDefaultEdgeStyle(style);

            //拖拽线图标
            mxConnectionHandler.prototype.connectImage = new mxImage('images/connector.gif', 16, 16);
            //组收缩按钮
            mxGraph.prototype.expandedImage = new mxImage('images/none.png', 1, 1);
            // //设置全局线样式
            // var style = this.graph.getStylesheet().getDefaultEdgeStyle();
            //允许移动
            this.graph.panningHandler.useLeftButtonForPanning = true;
            this.graph.panningHandler.ignoreCell = true;
            this.graph.container.style.cursor = 'move';
            this.graph.setPanning(false);  // 禁止移动
            //禁止编辑
            this.graph.setEnabled(false);
            //是否允许拖动
            this.graph.setCellsMovable(false);

            this.parent = this.graph.getDefaultParent();

            var track = new mxCellTracker(this.graph);
            track.mouseMove = function (sender, me) {
                var cell = this.getCell(me);
                if (cell && cell.isVertex() && cell.edges && cell.value != self.nodeData.systemAlias) {
                    //设置鼠标为样式为手状
                    me.getState().setCursor('pointer');
                }

                if (cell && cell.isEdge()) {
                    me.getState().setCursor('pointer');
                }
            };
        },
        _bindGraphEvent: function () {
            var self = this;
            //双击
            this.graph.addListener(mxEvent.CLICK, function (sender, evt) {
                var cell = evt.getProperty('cell');
                if (!cell) return;
                var id = cell.isVertex() ? cell.id : cell.target.id;
                var targetNode = self.vertexs[id];

                var clickEdge = function (cell) {

                    self.graph.getModel().beginUpdate();

                    try {
                        for (var i = 0; i < self.edges.length; i++) {
                            self.graph.setCellStyles(mxConstants.STYLE_STROKEWIDTH, "3", [self.edges[i]]);
                        }
                        self.graph.setCellStyles(mxConstants.STYLE_STROKEWIDTH, "6", [cell]);

                    } finally {
                        self.graph.getModel().endUpdate();
                    }

                    self.triggerEvent("clickEdge", targetNode);
                }
                if (cell != null && cell.edge) {
                    clickEdge(cell);
                }

                if (cell != null && cell.isVertex() && cell.value != self.nodeData.systemAlias && cell.edges) {
                    clickEdge(cell.edges[0]);
                }
            });
        },
        _clearGraphy: function () {
            var self = this;

            if (this.graph) {
                this.graph.destroy();
            }

        }

    });

    window.NodeType = DemoIndex.NodeType;
    window.NodeStatus = DemoIndex.NodeStatus;

    $.fn.extend({
        createGraphy: function (nodeData) {

            var instance = null;
            if ($(this).data("__instance__")) {
                $(this).data("__instance__").destoryGraphy();
            }

            instance = new DemoIndex.Base({
                $GraphyContainer: $(this),
                nodeData: nodeData
            });

            $(this).data("__instance__", instance)

            return instance;
        }
    });


})(jQuery);