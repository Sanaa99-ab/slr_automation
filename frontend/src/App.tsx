
// import React, { useState } from 'react';
// import './App.css';
// import Form from './components/form';
// import Results from './components/results';

// function App() {
//   const [results, setResults] = useState<any>(null);

//   return (
//     <div className="App container">
//       <h1 className="text-center my-4">SLR Automation</h1>
//       <Form onSubmit={setResults} />
//       <Results data={results} />
//     </div>
//   );
// }

// export default App;

import React, { useState } from 'react';
import './App.css';
import Form from './components/form';
import Results from './components/results';

function App() {
  // Hold your results state
  const [results, setResults] = useState<any>(null);
  // You can also track the current query if you want to allow a manual refresh
  const [currentQuery, setCurrentQuery] = useState<string>("");

  // onSubmit is called from the Form component; it receives the new results and also sets the current query
  const handleSubmit = (data: any, query: string) => {
    setCurrentQuery(query);
    setResults(data);
  };

  // Optionally, add a manual refresh function (re-triggering the query)
  const handleRefresh = async () => {
    // You might re-run the same API call here based on currentQuery.
    // For demonstration, we clear the results so the user knows to re-submit.
    setResults(null);
    // In a real implementation, you could call the API with currentQuery again.
  };

  return (
    <div className="App container">
      <h1 className="title">SLR Automation</h1>
      <Form onSubmit={handleSubmit} />
      {/* If you want a refresh button to re-run the last query */}
      {currentQuery && (
        <button className="btn-refresh" onClick={handleRefresh}>
          Refresh Results
        </button>
      )}
      <Results data={results} />
    </div>
  );
}


export default App;
