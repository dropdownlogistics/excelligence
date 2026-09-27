/* Excelligence path rule — the one traversal rule for learning paths.
   Stated in /standards/PATH-RULE.md; mirrored in mcp/excelligence_mcp.py.
   Used by /explorer/ (Path Finder) and /paths/ (per-step link labels).

   LEADS_TO    A -> B : traverse forward (A then B)
   DEPENDS_ON  A -> B : "A depends on B", so B comes first: traverse B -> A
   PAIRS_WITH  A -- B : both directions
   Shortest path: BFS, neighbours visited in ascending id order.
   prerequisites(X): transitive closure of X's DEPENDS_ON targets. */
(function (root) {
  "use strict";
  // When one step is joined by more than one relation, report the strongest.
  var PRECEDENCE = { LEADS_TO: 0, DEPENDS_ON: 1, PAIRS_WITH: 2 };

  // adjacency[from][to] = relation that lets a learner step from -> to
  function learningAdjacency(edges) {
    var adj = {};
    function add(a, b, rel) {
      if (!adj[a]) adj[a] = {};
      var cur = adj[a][b];
      if (cur === undefined || PRECEDENCE[rel] < PRECEDENCE[cur]) adj[a][b] = rel;
    }
    (edges || []).forEach(function (e) {
      if (e.type === "LEADS_TO") add(e.source, e.target, "LEADS_TO");
      else if (e.type === "DEPENDS_ON") add(e.target, e.source, "DEPENDS_ON");
      else if (e.type === "PAIRS_WITH") { add(e.source, e.target, "PAIRS_WITH"); add(e.target, e.source, "PAIRS_WITH"); }
    });
    return adj;
  }

  // relation joining step a -> step b under the rule, or null
  function stepRelation(adj, a, b) {
    return (adj[a] && Object.prototype.hasOwnProperty.call(adj[a], b)) ? adj[a][b] : null;
  }

  // shortest learning path start -> end as an array of ids, or null
  function shortestPath(adj, start, end) {
    if (start === end) return [start];
    var prev = {}, queue = [start], head = 0;
    prev[start] = null;
    while (head < queue.length) {
      var cur = queue[head++];
      var nbrs = Object.keys(adj[cur] || {}).sort();
      for (var i = 0; i < nbrs.length; i++) {
        var n = nbrs[i];
        if (Object.prototype.hasOwnProperty.call(prev, n)) continue;
        prev[n] = cur;
        if (n === end) {
          var path = [n];
          while (prev[path[0]] !== null) path.unshift(prev[path[0]]);
          return path;
        }
        queue.push(n);
      }
    }
    return null;
  }

  // transitive closure of id's DEPENDS_ON targets, sorted by id
  function prerequisites(edges, id) {
    var deps = {};
    (edges || []).forEach(function (e) {
      if (e.type === "DEPENDS_ON") (deps[e.source] = deps[e.source] || []).push(e.target);
    });
    var seen = {}, stack = [id];
    while (stack.length) {
      var cur = stack.pop();
      (deps[cur] || []).forEach(function (t) {
        if (t !== id && !seen[t]) { seen[t] = true; stack.push(t); }
      });
    }
    return Object.keys(seen).sort();
  }

  var api = { learningAdjacency: learningAdjacency, stepRelation: stepRelation, shortestPath: shortestPath, prerequisites: prerequisites };
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  root.PathRule = api;
})(typeof window !== "undefined" ? window : globalThis);
