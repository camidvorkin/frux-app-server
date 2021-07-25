"""Templates for pages."""

GRAPHIQL_TEMPLATE = """<!--
The request to this GraphQL server provided the header "Accept: text/html"
and as a result has been presented GraphiQL - an in-browser IDE for
exploring GraphQL.
If you wish to receive JSON, provide the header "Accept: application/json" or
add "&raw" to the end of the URL within a browser.
-->
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8" />
  <title>{{graphiql_html_title}}</title>
  <meta name="robots" content="noindex" />
  <meta name="referrer" content="origin" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <link href="data:image/x-icon;base64,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" rel="icon" type="image/x-icon" />
  <style>
    body {
      margin: 0;
      overflow: hidden;
    }
    #graphiql {
      height: 100vh;
    }
  </style>
  <link href="//cdn.jsdelivr.net/npm/graphiql@{{graphiql_version}}/graphiql.css" rel="stylesheet" />
  <script src="//cdn.jsdelivr.net/npm/promise-polyfill@8.1.3/dist/polyfill.min.js"></script>
  <script src="//cdn.jsdelivr.net/npm/unfetch@4.1.0/dist/unfetch.umd.js"></script>
  <script src="//cdn.jsdelivr.net/npm/react@16.13.1/umd/react.production.min.js"></script>
  <script src="//cdn.jsdelivr.net/npm/react-dom@16.13.1/umd/react-dom.production.min.js"></script>
  <script src="//cdn.jsdelivr.net/npm/graphiql@{{graphiql_version}}/graphiql.min.js"></script>
  <script src="//cdn.jsdelivr.net/npm/subscriptions-transport-ws@0.9.16/browser/client.js"></script>
  <script src="//cdn.jsdelivr.net/npm/graphiql-subscriptions-fetcher@0.0.2/browser/client.js"></script>
</head>
<body>
  <div id="graphiql">Loading...</div>
  <script>
    // Collect the URL parameters
    var parameters = {};
    window.location.search.substr(1).split('&').forEach(function (entry) {
      var eq = entry.indexOf('=');
      if (eq >= 0) {
        parameters[decodeURIComponent(entry.slice(0, eq))] =
          decodeURIComponent(entry.slice(eq + 1));
      }
    });
    // Produce a Location query string from a parameter object.
    function locationQuery(params) {
      return '?' + Object.keys(params).filter(function (key) {
        return Boolean(params[key]);
      }).map(function (key) {
        return encodeURIComponent(key) + '=' +
          encodeURIComponent(params[key]);
      }).join('&');
    }
    // Derive a fetch URL from the current URL, sans the GraphQL parameters.
    var graphqlParamNames = {
      query: true,
      variables: true,
      operationName: true
    };
    var otherParams = {};
    for (var k in parameters) {
      if (parameters.hasOwnProperty(k) && graphqlParamNames[k] !== true) {
        otherParams[k] = parameters[k];
      }
    }
    // Configure the subscription client
    let subscriptionsFetcher = null;
    var fetchURL = locationQuery(otherParams);
    // Defines a GraphQL fetcher using the fetch API.
    function graphQLFetcher(graphQLParams, opts) {
      return fetch(fetchURL, {
        method: 'post',
        headers: Object.assign(
          {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
          },
          opts && opts.headers,
        ),
        body: JSON.stringify(graphQLParams),
        credentials: 'include',
      }).then(function (response) {
        return response.json();
      });
    }
    // When the query and variables string is edited, update the URL bar so
    // that it can be easily shared.
    function onEditQuery(newQuery) {
      parameters.query = newQuery;
      updateURL();
    }
    function onEditVariables(newVariables) {
      parameters.variables = newVariables;
      updateURL();
    }
    function onEditHeaders(newHeaders) {
      parameters.headers = newHeaders;
      updateURL();
    }
    function onEditOperationName(newOperationName) {
      parameters.operationName = newOperationName;
      updateURL();
    }
    function updateURL() {
      history.replaceState(null, null, locationQuery(parameters));
    }
    // Render <GraphiQL /> into the body.
    ReactDOM.render(
      React.createElement(GraphiQL, {
        fetcher: subscriptionsFetcher || graphQLFetcher,
        onEditQuery: onEditQuery,
        onEditVariables: onEditVariables,
        onEditHeaders: onEditHeaders,
        onEditOperationName: onEditOperationName,

        query: {{ params.query|tojson }},
        response: {{ result|tojson }},
        variables: {{ params.variables|tojson }},
        operationName: {{ params.operation_name|tojson }},

        headers: {{params.headers or ''|tojson}},
        headerEditorEnabled: true,
        shouldPersistHeaders: true,
      }),
      document.getElementById('graphiql')
    );
  </script>
</body>
</html>"""
