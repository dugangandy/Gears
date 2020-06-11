/**
 * Created by hankskfc on 2017/4/12.
 */

(function ($) {

    var chain = {};

    chain.TimeProcess = $.Base.Event.extend({
        init: function (pOpts) {
            $.extend(true, this, {
                $container: null,
                baseTimeWidth: -1,
                perDepthWidthIncrease: -1,
                getTimeProgressContainer: function ($container) {
                    return $container.find(".time_progress");
                },
                getSpanTitleContainer: function ($container) {
                    return $container.find(".span_title");
                },
                getSpanContainer: function ($container) {
                    return $container.find(".span");
                },
                formatItemFunc: function (row, rowList) {
                    return row;
                },
                getTimeProgressHeader: function ($container) {
                    return $container.find("thead tr>td:eq(2)")
                }
            }, pOpts);

            this.trs = {};
            this.trTree = [];
            this.data = [];
            this.brotherDic = {};
            this.dataDic = {};
        },
        setBaseTimeWidth: function (w) {
            this.baseTimeWidth = w;
        },
        setPerDepthWidthIncrease: function (w) {
            this.perDepthWidthIncrease = w;
        },
        render: function () {
            var self = this;

            var rawData = this._getTrData();
            this._formatInputData(rawData);
            this._formatTr();
            this._renderTr();

            rawData = this._getTrData();
            this._formatInputData(rawData);


            //设置时间轴大小
            if (this.baseTimeWidth != -1) {
                var w = 0;
                if (this.perDepthWidthIncrease != -1) {
                    var maxDepth = 0;
                    $.each(this.data, function (index, item) {
                        if (maxDepth < item.depth) {
                            maxDepth = item.depth;
                        }
                    })
                    w = maxDepth * this.perDepthWidthIncrease;
                }


                this.getTimeProgressHeader(this.$container).css("width", this.baseTimeWidth + w + "px");
            }

            $.each(this.data, function (index, row) {
                var tr = self.trs[self._getTrsKey(row)];
                //设置title
                var spanTitle = self.getSpanTitleContainer(tr);
                spanTitle.attr("title", spanTitle.val());

                //设置spanPlace
                var spanContainer = self.getSpanContainer(tr);
                var spanPlaceHtml = self._createSpanPlace(row);
                spanContainer.prepend(spanPlaceHtml);

                self._calcTimeW(row);
            });

            $.each(this.data, function (index, row) {
                var tr = self.trs[self._getTrsKey(row)];
                //设置时间轴的宽度偏移度
                var timeprogress = self.getTimeProgressContainer(tr);
                var m = self._calcTimeMarginLeft(row);
                timeprogress.css({
                    width: row._w + "%",
                    "margin-left": m + "%"
                });

            });

            this.renderCollapse();
        },
        renderCollapse: function () {
            var self = this;

            $.each(this.data, function (index, row) {
                var hasChild = _.findIndex(self.data, function (item) {
                    return row.id == item.pid;
                });

                if (hasChild != -1) {
                    var tr = row.trObj;
                    self._collapse(tr, row);

                }
            })
        },
        setFormatItem: function (formatItemFunc) {
            this.formatItemFunc = formatItemFunc;
        },
        _collapse: function ($tr, data) {
            var self = this,
                iIcon = $tr.find(".span i");
            //是否展开
            iIcon.prop("collapse", false);

            iIcon.css("cursor", "pointer");

            iIcon.on("click", function () {
                var isCollapse = iIcon.prop("collapse") === true;

                var childrenTrs = self._findAllChildren(data);
                // 折叠
                if (!isCollapse) {
                    $.each(childrenTrs, function (i, r) {
                        r.trObj.hide("normal");
                    });
                    iIcon.addClass("fa-plus");
                    iIcon.removeClass("fa-minus");
                // 展开
                } else {
                    $.each(childrenTrs, function (i, r) {
                        r.trObj.show("normal");
                        r.trObj.find(".span i").addClass("fa-minus");
                        r.trObj.find(".span i").removeClass("fa-plus");
                    });

                    iIcon.addClass("fa-minus");
                    iIcon.removeClass("fa-plus");
                }

                iIcon.prop("collapse", !isCollapse);
            });
        },
        _findRoot: function() {
            var root;
            for (var key in this.dataDic) {
                var value = this.dataDic[key];
                if (root == undefined) {
                    root = value
                } else {
                    if (value.depth < root.depth) {
                        root = value
                    }
                }
            }
            return root;
        },
        _findAllChildren: function (root) {
            var self = this;
            var childrenTrs = [];

            var tmps = _.filter(self.data, function (item) {
                return root.id == item.pid;
            });

            if (tmps.length > 0) {
                $.each(tmps, function (i, r) {
                    childrenTrs.push(r);

                    var c = self._findAllChildren(r);

                    $.each(c, function (ii, rr) {
                        childrenTrs.push(rr);
                    })
                })
            }

            return childrenTrs;
        },
        _createSpanPlace: function (row) {
            //<span class="span_place"></span>
            var root = this._findRoot();
            if (row.depth == root.depth) return "";

            var ret = [];
            for (var i = 0; i < row.depth - root.depth; i++) {
                ret.push('<span class="span_place"></span>');
            }

            return ret.join(" ");
        },
        _calcTimeW: function (row) {

            // if (row.pid == -1) {
            var root = this._findRoot();
            if (row.pid == root.pid) {

                row._w = 100;

                return 100;
            }


            var pRow = this.dataDic[row.pid];
            // var root = _.find(this.dataDic, function (item) {
            //     return item.pid == -1;
            // });


            //假设上一层已经画完
            //pRow._w;
            var w = row.cost * pRow._w / pRow.cost;
            if (w > 2) w -= 2;

            //当前行宽度大于父的宽度
            //异步线程案例 设置为1
            if (w > pRow._w) {
                w = 1;
            }

            row._w = Math.max(w, 1);//+ 2 * child.length;

            return w;

        },
        _calcTimeMarginLeft: function (row) {
            var self = this;

            var root = this._findRoot();
            if (row.pid == root.pid) {
            // if (row.pid == -1) {
                row._marginLeft = 0;
                return 0;
            }

            if (row.id == 2) {
                row._marginLeft = 2;
                return 2;
            }

            var brotherAll = _.filter(this.data, function (item) {
                return row.depth == item.depth && item.pid == row.pid;
            })

            var bM = (row.depth - 1) * 2;

            //从上往下渲染
            var b = -1;
            var c = 0;
            var x = 0;

            //计算相对于父容器的偏移度
            for (var i = 0; i < brotherAll.length; i++) {
                var item = brotherAll[i];
                c = i;
                b = i - 1;

                if (brotherAll[c]._marginLeft == undefined) {
                    //第一个
                    if (b != -1) {
                        bM = x + 2;
                    } else {
                        bM = 2;
                    }

                    break;
                }
                x += item._w;
            }

            var pRow = this.dataDic[row.pid];

            var v = bM + pRow._marginLeft;

            row._marginLeft = v;
            return v;
        },
        _getTrsKey: function (item) {
            return item.id;
        },
        _getDataDicKey: function (item) {
            return item.id;
        },
        _getTrData: function () {
            var self = this;

            var trlist = this.$container.find("tr");
            var data = [];
            $.each(trlist, function (index, item) {
                var d = $(item).data("json");
                if (d) {
                    d.trObj = $(item);
                    data.push(d);
                }
            });

            return data;
        },
        _clear: function () {
            this.trs = {};
            this.data = [];
            this.dataDic = {};
        },
        _addDataItem: function (item) {
            this.data.push(item);
            this.dataDic[this._getDataDicKey(item)] = item;

        },
        _formatInputData: function (data) {
            var self = this;
            //data ---> []
            //item ---> {pid:1,cost:25,id:1,trObj:{}}
            this._clear();

            $.each(data, function (index, item) {
                var d = self.formatItemFunc(item, data);
                self.trs[d.id] = d.trObj;
                self._addDataItem(d);
            });

            // return [
            //     {pid: -1, cost: 25, id: 1, depth: 1,logtime:111111},
            //     {pid: 1, cost: 10, id: 2, depth: 2,logtime:111111},
            //     {pid: 2, cost: 5, id: 3, depth: 3,logtime:111111},
            //     {pid: 2, cost: 5, id: 4, depth: 3,logtime:111111},
            //     {pid: 1, cost: 10, id: 5, depth: 2,logtime:111111},
            //     {pid: 5, cost: 5, id: 6, depth: 3,logtime:111111},
            //     {pid: 5, cost: 5, id: 7, depth: 3,logtime:111111},
            //     {pid: 1, cost: 5, id: 8, depth: 3,logtime:111111}
            // ];
        },

        _formatTr: function () {

            var self = this;
            var root = undefined;
            this.trTree = [];
            var root = this._findRoot();
            // for (var key in this.dataDic) {
            //     var value = this.dataDic[key];
            //     if (root == undefined) {
            //         root = value
            //     } else {
            //         if (value.depth < root.depth) {
            //             root = value
            //         }
            //     }
            // }
            // var root = _.find(this.dataDic, function (item) {
            //     return item.pid == -1;
            // })
            this.trTree.push(root);

            if (!root) {
                // console.log("cann't find the pid(-1)");
                console.log("cann't find the root node.");
                return;
            }
            this._findTrChildren(root);

        },
        _findTrChildren: function (root) {
            var self = this;

            var children = _.filter(this.dataDic, function (item) {
                return item.pid == root.id;
            });

            if (children.length <= 0) return;

            children = _.sortBy(children, function (item) {
                return item.logtime || 0;
            });

            $.each(children, function (i, item) {
                self.trTree.push(item);
                self._findTrChildren(item);
            });
        },
        _renderTr: function () {
            var self = this;
            var parent = this.$container.parent();

            var headTr = this.$container.find("tr:eq(0)");
            var table = $("<table class=\"table\"></table>");
            var h = $("<thead></thead>");
            headTr.appendTo(h);
            h.appendTo(table);

            var body = $("<tbody></tbody>");

            $.each(this.trTree, function (index, item) {
                item.trObj.appendTo(body);
            })

            body.appendTo(table);

            table.appendTo(parent);
            this.$container.remove();
            this.$container = table;

            table.show();

        }
    });


    $.fn.extend({
        chain: function (option) {
            option = option || {};
            if ($(this).prop("__chain_instance__")) {
                return $(this).prop("__chain_instance__");
            }

            var instance = new chain.TimeProcess({
                $container: $(this),
                baseTimeWidth: option.baseTimeWidth || -1,
                perDepthWidthIncrease: option.perDepthWidthIncrease || -1
            });

            $(this).prop("__chain_instance__");

            return instance;
        }
    });

})(jQuery)
