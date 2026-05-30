(function() {
  "use strict";
  var INDEX_URL = "search.json";
  var DEBOUNCE = 300;
  var MAX_RESULTS = 10;
  var index = null;
  var searchInput = null;
  var resultsContainer = null;
  var debounceTimer = null;

  function esc(s) {
    if (s == null) return "";
    return String(s).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;");
  }

  function highlight(text, query) {
    if (!query) return esc(text);
    var re = new RegExp("(" + query.replace(/[.*+?^${}()|[\]\\]/g, "\\$&") + ")", "gi");
    return esc(text).replace(re, "<mark>$1</mark>");
  }

  function tokenize(text) {
    return text.toLowerCase().split(/\W+/).filter(function(t){return t.length>0;});
  }

  function scoreItem(item, tokens) {
    var title = (item.title || "").toLowerCase();
    var content = (item.content || "").toLowerCase();
    var tags = (item.tags || []).join(" ").toLowerCase();
    var s = 0;
    tokens.forEach(function(t) {
      if (title.indexOf(t) >= 0) s += 10;
      if (tags.indexOf(t) >= 0) s += 5;
      if (content.indexOf(t) >= 0) s += 1;
    });
    return s;
  }

  function doSearch(query) {
    if (!index || !query || query.trim().length < 2) {
      if (resultsContainer) resultsContainer.innerHTML = "";
      return;
    }
    var tokens = tokenize(query);
    if (tokens.length === 0) { resultsContainer.innerHTML = ""; return; }
    var all = [];
    if (index.pages) index.pages.forEach(function(p){ all.push(p); });
    if (index.posts) index.posts.forEach(function(p){ all.push(p); });
    var scored = all.map(function(item) {
      return { item: item, score: scoreItem(item, tokens) };
    }).filter(function(x){ return x.score > 0; });
    scored.sort(function(a,b){ return b.score - a.score; });
    var results = scored.slice(0, MAX_RESULTS);
    renderResults(results, query);
  }

  function renderResults(results, query) {
    if (!resultsContainer) return;
    if (results.length === 0) {
      resultsContainer.innerHTML = "<div class=\"search-no-results\">No results found for <strong>" + esc(query) + "</strong></div>";
      return;
    }
    var html = "<div class=\"search-results-list\">";
    results.forEach(function(r) {
      var item = r.item;
      var label = item.type === "post" ? "Post" : "Page";
      var excerpt = (item.content || "").substring(0, 150);
      html += "<a class=\"search-result-item\" href=\"" + esc(item.url) + "\">";
      html += "<div class=\"search-result-type\">" + label + "</div>";
      html += "<div class=\"search-result-title\">" + highlight(item.title, query) + "</div>";
      html += "<div class=\"search-result-excerpt\">" + highlight(excerpt, query) + "</div>";
      if (item.tags && item.tags.length) {
        html += "<div class=\"search-result-tags\">" + item.tags.map(function(t){return "<span class=\"search-tag\">"+esc(t)+"</span>";}).join(" ") + "</div>";
      }
      html += "</a>";
    });
    html += "</div>";
    resultsContainer.innerHTML = html;
  }

  function initSearch() {
    searchInput = document.getElementById("search-input");
    resultsContainer = document.getElementById("search-results");
    if (!searchInput || !resultsContainer) return;
    fetch(INDEX_URL)
      .then(function(r) { return r.json(); })
      .then(function(data) { index = data; })
      .catch(function(e) { console.error("Search index failed:", e); });
    searchInput.addEventListener("input", function() {
      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(function() { doSearch(searchInput.value); }, DEBOUNCE);
    });
    searchInput.addEventListener("keydown", function(e) {
      if (e.key === "Escape") {
        searchInput.value = "";
        resultsContainer.innerHTML = "";
        searchInput.blur();
      }
    });
    document.addEventListener("click", function(e) {
      if (!searchInput.contains(e.target) && !resultsContainer.contains(e.target)) {
        resultsContainer.innerHTML = "";
      }
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initSearch);
  } else {
    initSearch();
  }
})();
