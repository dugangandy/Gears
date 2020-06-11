(function ($) {
    var TopologyIndex = {
        QueryTable: null,
        Graphy: null
    };
    //window.appName = "sales.order.receivable.api";

    TopologyIndex.Base = $.Base.Event.extend({
        init: function (pOpts) {
            $.extend(true, this, {
                $RootContainer: null,
                $GraphyContainer: null
                // $SearchContainer: null,
                // $QueryTableContainer: null
            }, pOpts);

            this.setOptions();
        },
        setOptions: function () {
            var self = this;


            this.graphy = new TopologyIndex.Graphy({
                $container: self.$GraphyContainer,
                $base: self,
                mask: self.mask
            });


            //点击边
            this.graphy.addEvent("clickEdge", function (data) {
                // self.queryTable.queryData(data.from, data.to);
                console.log(data);
                // 打开方法详情页面
                openDetail(data.from, data.to);
            });
        },
        getQueryObj: function () {
            return {
                appName: window.appName
            };
        },
        query: function () {
            var data = this.$RootContainer.data("json");
            this.graphy.render(data);
        }
    });

    TopologyIndex.Graphy = $.Base.Event.extend({
        init: function (pOpts) {

            $.extend(true, this, {
                $container: null
            }, pOpts);

            this.setOptions();
        },
        setOptions: function () {
            var self = this;

            this.graph = null;
            this.model = null;
            this.nodeList = [];
            this.edgeOutList = [];
            this.edgeInList = [];

            this.newEvent("drawNode");
            this.addEvent("drawNode", function (nodeInfo) {
                self.drawNode(nodeInfo);
            });

            this.newEvent("drawEdge");
            this.addEvent("drawEdge", function (edgeInfo) {
                self.drawEdge(edgeInfo);
            });

            this.newEvent("clickEdge");

            //存去 mxGraph的vertex信息+orginalPoint起始坐标
            this.drawNodeList = {};
            this.nodeStyle = {
                width: 280,
                height: 40,
                marginTop: 20,
                marginLeft: 100,
                orginalPoint: {x: 10, y: 60}
            };
            this.nodeIdGenerator = (function () {
                var count = 0;
                return {
                    next: function () {
                        count++;
                        return count;
                    }
                }
            })();
        },
        initConfig: function () {
            var self = this;

            this.node = this.$container[0];
            this.model = new mxGraphModel();
            this.graph = new mxGraph(this.node, this.model);
            this.graph.setConnectable(true);
            this.edges = [];
            this.vertexts = [];

            // Creates the default style for vertices
            var style = [];
            style[mxConstants.STYLE_SHAPE] = mxConstants.SHAPE_RECTANGLE;
            style[mxConstants.STYLE_PERIMETER] = mxPerimeter.RectanglePerimeter;
            style[mxConstants.STYLE_STROKECOLOR] = 'gray';
            style[mxConstants.STYLE_ROUNDED] = true;
            style[mxConstants.STYLE_FILLCOLOR] = '#EEEEEE';
            style[mxConstants.STYLE_GRADIENTCOLOR] = 'white';
            style[mxConstants.STYLE_FONTCOLOR] = '#774400';
            style[mxConstants.STYLE_ALIGN] = mxConstants.ALIGN_CENTER;
            style[mxConstants.STYLE_VERTICAL_ALIGN] = mxConstants.ALIGN_MIDDLE;
            style[mxConstants.STYLE_FONTSIZE] = '14';
            style[mxConstants.STYLE_FONTSTYLE] = 1;
            this.graph.getStylesheet().putDefaultVertexStyle(style);

            // Creates the default style for edges
            style = [];
            style[mxConstants.STYLE_SHAPE] = mxConstants.SHAPE_CONNECTOR;
            style[mxConstants.STYLE_STROKECOLOR] = '#6482B9';
            style[mxConstants.VERTEX_SELECTION_STROKEWIDTH] = "20";
            style[mxConstants.STYLE_ALIGN] = mxConstants.ALIGN_BOTTOM;
            style[mxConstants.STYLE_VERTICAL_ALIGN] = mxConstants.ALIGN_LEFT;
            style[mxConstants.STYLE_EDGE] = mxEdgeStyle.ElbowConnector;//mxEdgeStyle.ElbowConnector;
            style[mxConstants.STYLE_ENDARROW] = mxConstants.ARROW_OPEN;//mxConstants.ARROW_CLASSIC;
            style[mxConstants.STYLE_FONTSIZE] = '12';
            this.graph.getStylesheet().putDefaultEdgeStyle(style);

            //拖拽线图标
            mxConnectionHandler.prototype.connectImage = new mxImage('images/connector.gif', 16, 16);
            //组收缩按钮
            mxGraph.prototype.expandedImage = new mxImage('images/none.png', 1, 1);
            //设置全局线样式
            var style = this.graph.getStylesheet().getDefaultEdgeStyle();
            //允许移动
            this.graph.panningHandler.useLeftButtonForPanning = false;
            this.graph.panningHandler.ignoreCell = true;
            this.graph.container.style.cursor = 'cursor';
            this.graph.setPanning(true);
            //禁止编辑
            this.graph.setEnabled(false);
            //是否允许连接线
            this.graph.setConnectable(true);
            //是否允许编辑
            this.graph.setCellsEditable(false);
            //是否允许拖动
            this.graph.setCellsMovable(true);
            //多选
            //new mxRubberband(this.graph);
            this.parent = this.graph.getDefaultParent();
            mxCell.prototype.setData = function (pObj) {
                this["json"] = pObj;
            }
            //是否开启拖动导航
            mxGraphHandler.prototype.guidesEnabled = false;
            // 去锯齿效果
            mxRectangleShape.prototype.crisp = false;
            // 设置自动扩大鼠标悬停
            this.graph.panningHandler.autoExpand = true;
            // 禁用浏览器自带右键菜单
            mxEvent.disableContextMenu(this.node);

            var track = new mxCellTracker(this.graph);
            track.mouseMove = function (sender, me) {
                var cell = this.getCell(me);
                var queryObj = self.$base.getQueryObj();
                if (cell && cell.isVertex() && cell.edges && cell.value != queryObj.appName) {
                    //设置鼠标为样式为手状
                    me.getState().setCursor('pointer');
                }

                if (cell && cell.isEdge()) {
                    me.getState().setCursor('pointer');
                }
            };

            // 覆写右键单击事件
            this.graph.panningHandler.factoryMethod = function (menu, cell, evt) {
                /* menu.addItem('放大(+)',null,function(){
                 _this.graph.zoomIn();
                 });
                 menu.addItem('缩小(-)',null,function(){
                 _this.graph.zoomOut();
                 });
                 menu.addItem('删除已选元素', null, function () {
                 _this.graph.removeCells(_this.graph.getSelectionCells());
                 return false;
                 });
                 menu.addItem('删除所有元素', null, function () {
                 _this.graph.removeCells(_this.graph.getChildVertices(_this.graph.getDefaultParent()));
                 return false;
                 });
                 menu.addItem('保存表单', null, function () {
                 _this.save();
                 return false;
                 });
                 menu.addItem('加载上一次的XML',null,function(){
                 _this.loadXML();
                 return false;
                 });
                 */
            };
        },
        bindGraphEvent: function () {
            var self = this;
            //双击
            this.graph.addListener(mxEvent.CLICK, function (sender, evt) {
                var cell = evt.getProperty('cell');
                var queryObj = self.$base.getQueryObj();
                var clickEdge = function (cell) {

                    var fromServiceAlias = _.find(self.nodeList, function (it) {
                        return it.nodeName == cell.source.value
                    });
                    var toServiceAlias = _.find(self.nodeList, function (it) {
                        return it.nodeName == cell.target.value
                    });

                    self.graph.getModel().beginUpdate();

                    try {
                        for (var i = 0; i < self.edges.length; i++) {
                            self.graph.setCellStyles(mxConstants.STYLE_STROKEWIDTH, "2", [self.edges[i]]);
                        }
                        self.graph.setCellStyles(mxConstants.STYLE_STROKEWIDTH, "5", [cell]);

                    } finally {
                        self.graph.getModel().endUpdate();
                    }


                    self.triggerEvent("clickEdge", {
                        from: {
                            nodeName: fromServiceAlias.nodeName,
                            nodeType: fromServiceAlias.nodeCategory
                        }, to: {
                            nodeName: toServiceAlias.nodeName,
                            nodeType: toServiceAlias.nodeCategory
                        }
                    });
                }
                if (cell != null && cell.edge) {
                    clickEdge(cell);
                }

                if (cell != null && cell.isVertex() && cell.value != queryObj.appName && cell.edges) {
                    clickEdge(cell.edges[0]);
                }
            });
        },
        drawNode: function (nodeInfo) {
            //原型
            //fromNode,toNode,cost,brotherNodes
            var self = this;
            var fromVertex = this.drawNodeList[nodeInfo.fromNode.nodeId];
            if (!fromVertex) {
                var maxX = 0;
                if (nodeInfo.parentNodes) {
                    $.each(nodeInfo.parentNodes, function (i, item) {
                        var tmpVertex = self.drawNodeList[item.nodeId];
                        if (tmpVertex && tmpVertex.orginalPoint && tmpVertex.orginalPoint.x > maxX) {
                            maxX = tmpVertex.orginalPoint.x;
                        }
                    });
                }

                var vertex = this._insertVertex({
                    fromVertex: fromVertex,
                    id: nodeInfo.fromNode.nodeId,
                    name: nodeInfo.fromNode.nodeName,
                    initPoint: self._calcInitPoint({
                        x: maxX,
                        y: 0
                    }, nodeInfo.brotherNodes, nodeInfo.parentNodes, nodeInfo.fromNode)
                });

                this.vertexts.push(vertex);
            }
        },
        drawEdge: function (edgeInfo) {
            var fromVertex = this.drawNodeList[edgeInfo.fromNodeId];
            var toVertex = this.drawNodeList[edgeInfo.toNodeId];
            var x = fromVertex.geometry.x + this.nodeStyle.width + 20;
            var y = fromVertex.geometry.y - 5;
            var appName = this.$base.getQueryObj().appName;
            if (fromVertex.value == appName) {
                x = toVertex.geometry.x - 40;
                y = toVertex.geometry.y - 5;
            }
            this.graph.insertVertex(this.parent, null, edgeInfo.cost.callCount, x, y, 30, 20, "shape=image;strokeColor=#000;fillColor=#ccc;fontSize=13;fontStyle=3");

            var style = "perimeterSpacing=1;strokeWidth=2;labelBackgroundColor=green;fontStyle=1";
            if (edgeInfo.fromNodeId == edgeInfo.toNodeId) {
                style = "Loop;strokeWidth=2;labelBackgroundColor=green;fontStyle=1;";
            }
            var edge = this.graph.insertEdge(this.parent,
                null,
                null,
                fromVertex,
                toVertex,
                style);

            this.edges.push(edge);
        },
        render: function (data) {
            var self = this;
            this._clearGraphy();

            this._formatGraphyData(data);

            if (!mxClient.isBrowserSupported()) {
                mxUtils.error('Browser is not supported!', 200, false);
            } else {
                this.initConfig();
                this.bindGraphEvent();
                this._draw();
            }
        },
        _getStyleByNodeCategory: function (nodeInfo, appName) {

            if (nodeInfo.nodeName !== appName && nodeInfo.nodeCategory !== "soa") {
                return "rounded;strokeColor=#693;fillColor=#693;cursor:point";
            }
            return "rounded;strokeColor=#000;fillColor=#ccc;cursor:point";
        },
        _clearGraphy: function () {
            var self = this;

            if (this.graph) {
                this.graph.destroy();
            }

        },
        _formatGraphyData: function (data) {
            var self = this;
            //赋值这三个
            this.nodeList = [];
            this.edgeOutList = [];
            this.edgeInList = [];

            $.each(data, function (i, item) {
                var consumer = self._addNodeInfo(item.consumer, "left");
                var provider = self._addNodeInfo(item.provider, "right");

                self._addEdgeInfo(consumer, provider, item.callCount);
            });

            $.each(this.nodeList, function (i, item) {

                var out = _.find(self.edgeOutList, function (it) {
                    return it.nodeId == item.nodeId;
                });
                if (!out) {
                    self.edgeOutList.push({
                        nodeId: item.nodeId,
                        first: [{cost: null, nodeId: -1}]
                    });
                }

                var inEdge = _.find(self.edgeInList, function (it) {
                    return it.nodeId == item.nodeId;
                });

                if (!inEdge) {
                    self.edgeInList.push({
                        nodeId: item.nodeId,
                        first: [{cost: null, nodeId: -1}]
                    });
                }

            });
        },
        _addNodeInfo: function (node, type) {
            var self = this;
            var queryObj = self.$base.getQueryObj();
            if (node.name == queryObj.appName) type = "both";

            var nodeObj = _.find(this.nodeList, function (item) {
                return item.nodeName == node.name && item.nodeType == type;
            });

            if (!nodeObj) {
                nodeObj = {
                    nodeName: node.name,
                    nodeType: type,
                    nodeCategory: node.type,
                    nodeId: this.nodeIdGenerator.next()
                };
                this.nodeList.push(nodeObj);
            }

            return nodeObj;
        },
        _addEdgeInfo: function (consumer, provider, callCount) {
            var self = this;
            var cost = {callCount: callCount};
            //出度
            var out = self._findEdgeOut(consumer.nodeId);
            if (out) {
                var first = out.first;
                var tmp = _.find(first, function (item) {
                    return item.nodeId == provider.nodeId;
                });
                if (!tmp) {
                    out.first.push({
                        cost: cost,
                        nodeId: provider.nodeId
                    });
                }
            } else {
                this.edgeOutList.push({
                    nodeId: consumer.nodeId,
                    first: [{
                        cost: cost,
                        nodeId: provider.nodeId
                    }]
                });
            }

            //入度
            var inEdge = self._findEdgeIn(provider.nodeId);

            if (inEdge) {
                var first = inEdge.first;
                var tmp = _.find(first, function (item) {
                    return item.nodeId == consumer.nodeId;
                });
                if (!tmp) {
                    inEdge.first.push({
                        cost: cost,
                        nodeId: consumer.nodeId
                    });
                }
            } else {
                this.edgeInList.push({
                    nodeId: provider.nodeId,
                    first: [{
                        cost: cost,
                        nodeId: consumer.nodeId
                    }]
                });
            }

        },
        _findEdgeOut: function (nodeId) {
            return _.find(this.edgeOutList, function (item) {
                return item.nodeId == nodeId;
            });
        },
        _findEdgeIn: function (nodeId) {
            return _.find(this.edgeInList, function (item) {
                return item.nodeId == nodeId;
            });
        },
        _draw: function () {
            var self = this;
            //清空,重新render
            this.drawNodeList = {};

            //画节点
            $.each(this.edgeOutList, function (i, item) {
                $.each(item.first, function (j, it) {

                    var fromNode = _.find(self.nodeList, function (ii) {
                        return ii.nodeId == item.nodeId;
                    });
                    var brotherNode = null;
                    if (item.first.length == 1 && item.first[0].nodeId == -1) {//出度
                        var nextNode = _.find(self.edgeInList, function (iii) {
                            return iii.nodeId == item.nodeId
                        });
                        if (nextNode) {
                            brotherNode = _.find(self.edgeOutList, function (iii) {
                                return iii.nodeId == nextNode.first[0].nodeId;
                            });
                        }
                    }

                    var parentNode = _.find(self.edgeInList, function (iii) {
                        return iii.nodeId == item.nodeId;
                    });
                    if (parentNode && parentNode.first.length == 1 && parentNode.first[0].nodeId == -1) {//入度
                        brotherNode = _.find(self.edgeInList, function (iii) {
                            return iii.nodeId == it.nodeId;
                        });
                    }

                    var toNode = null;
                    if (it.nodeId != -1) {
                        toNode = _.find(self.nodeList, function (ii) {
                            return ii.nodeId == it.nodeId;
                        });
                    }

                    if (parentNode && parentNode.first.length == 1 && parentNode.first[0].nodeId == -1) {
                        parentNode = null;
                    }

                    self.triggerEvent("drawNode", {
                        fromNode: fromNode,
                        toNodeId: toNode,
                        brotherNodes: brotherNode ? brotherNode.first : null,
                        parentNodes: parentNode ? parentNode.first : null
                    });
                });
            });

            //画边
            $.each(this.edgeOutList, function (i, item) {
                $.each(item.first, function (j, it) {
                    var fromNode = _.find(self.nodeList, function (ii) {
                        return ii.nodeId == item.nodeId;
                    });

                    if (it.nodeId != -1) {
                        var toNode = _.find(self.nodeList, function (ii) {
                            return ii.nodeId == it.nodeId;
                        });
                        if (toNode) {
                            self.triggerEvent("drawEdge", {
                                fromNodeId: fromNode.nodeId,
                                toNodeId: toNode.nodeId,
                                cost: it.cost
                            });
                        }
                    }
                });
            });
        },
        //fromVertex,name,initPoint,id,style,
        _insertVertex: function (vertexInfo) {
            var self = this;
            var initPoint = vertexInfo.initPoint || this.nodeStyle.orginalPoint;
            var node = _.find(this.nodeList, function (item) {
                return item.nodeId == vertexInfo.id;
            });
            var appName = this.$base.getQueryObj().appName;

            var style = this._getStyleByNodeCategory(node, appName);//vertexInfo.style || "rounded;strokeColor=#000;fillColor=#ccc;cursor:point";

            var vertex = this.graph.insertVertex(vertexInfo.fromVertex || this.parent, null, vertexInfo.name,
                initPoint.x, initPoint.y, this.nodeStyle.width, this.nodeStyle.height, style);
            vertex.orginalPoint = initPoint;

            this.drawNodeList[vertexInfo.id] = vertex;
        },
        _calcInitPoint: function (orginalPoint, brotherNodes, parentNodes, currentNode) {
            orginalPoint = orginalPoint || this.nodeStyle.orginalPoint;
            var point = {x: orginalPoint.x, y: orginalPoint.y};

            if (point.y == 0) {
                point.y += this.nodeStyle.orginalPoint.y;
            }

            if (parentNodes) {
                //排除自反节点
                var selfInter = _.find(parentNodes, function (iii) {
                    return iii.nodeId == currentNode.nodeId;
                })
                var length = parentNodes.length;
                if (selfInter) length--;
                var h = (length - 1) * this.nodeStyle.height + (length - 1) * this.nodeStyle.marginTop;
                h = ~~(h / 2);
                point.y += h;
            }

            var index = _.findIndex(brotherNodes, function (it) {
                    return it.nodeId == currentNode.nodeId;
                }) + 1;

            if (index > 0) {
                point.y += (index - 1) * this.nodeStyle.marginTop + (index - 1) * this.nodeStyle.height;
            }

            if (point.x != 0) {
                point.x += this.nodeStyle.width;
            }

            point.x += this.nodeStyle.marginLeft;

            return point;
        }

    });

   $.TopologyIndex = TopologyIndex;
})(jQuery);