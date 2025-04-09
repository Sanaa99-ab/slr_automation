
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

// import React, { useState } from 'react';
// import './App.css';
// import Form from './components/form';
// import Results from './components/results';

// function App() {
//   // Hold your results state
//   const [results, setResults] = useState<any>(null);
//   // You can also track the current query if you want to allow a manual refresh
//   const [currentQuery, setCurrentQuery] = useState<string>("");

//   // onSubmit is called from the Form component; it receives the new results and also sets the current query
//   const handleSubmit = (data: any, query: string) => {
//     setCurrentQuery(query);
//     setResults(data);
//   };

//   // Optionally, add a manual refresh function (re-triggering the query)
//   const handleRefresh = async () => {
//     // You might re-run the same API call here based on currentQuery.
//     // For demonstration, we clear the results so the user knows to re-submit.
//     setResults(null);
//     // In a real implementation, you could call the API with currentQuery again.
//   };

//   return (
//     <div className="App container">
//       <h1 className="title">SLR Automation</h1>
//       <Form onSubmit={handleSubmit} />
//       {/* If you want a refresh button to re-run the last query */}
//       {currentQuery && (
//         <button className="btn-refresh" onClick={handleRefresh}>
//           Refresh Results
//         </button>
//       )}
//       <Results data={results} />
//     </div>
//   );
// }


// export default App;

// App.tsx
// App.tsx
import React, { useState } from 'react';
import './App.css';
import Form from './components/form';
import ResearchQuestions from './components/researchQuestions';
import ResearchQueries from './components/researchQueries';
import ScraperResultsTable from './components/ScraperResultsTable';
import axios from 'axios';

function App() {
  // States for LLM outputs
  const [researchQuestions, setResearchQuestions] = useState<string[]>([]);
  const [researchQueries, setResearchQueries] = useState<string[]>([]);
  const [loadingQuestions, setLoadingQuestions] = useState(false);
  const [loadingQueries, setLoadingQueries] = useState(false);
  
  // New state for scraper results
  const [scrapedRecords, setScrapedRecords] = useState<any[]>([]);
  const [loadingScrape, setLoadingScrape] = useState(false);

  // Function to be called when the form is submitted.
  // The 'query' will be used for the LLM processes and the scraper.

  const handleFormSubmit = async (query: string) => {
    // Clear previous results:
    setResearchQuestions([]);
    setResearchQueries([]);
    setScrapedRecords([]); // if used for scraper results
  
    // --- Phase 1: Generate Research Questions ---
    setLoadingQuestions(true);
    let questions: string[] = [];
    try {
      const response = await axios.post("http://127.0.0.1:5000/api/generate-questions", { topic: query });
      questions = response.data.questions; // store in local variable
      setResearchQuestions(questions);
    } catch (error) {
      console.error("Error generating research questions:", error);
      setResearchQuestions([]);
    }
    setLoadingQuestions(false);
  
    // If no research questions were returned, assign a fallback value
    if (questions.length === 0) {
      console.warn("No research questions returned; using fallback.");
      questions = [`Fallback: What is the impact of ${query}?`];
      setResearchQuestions(questions);
    }
  
  // --- Phase 2: Generate Search Queries ---
    
    setLoadingQueries(true);
    try {
      const response = await axios.post("http://127.0.0.1:5000/api/generate-queries", { topic: query, questions });
      setResearchQueries(response.data.queries);
    } catch (error) {
      console.error("Error generating search queries:", error);
      setResearchQueries([]);
    }
    setLoadingQueries(false);
    
    
    // --- Phase 3: Scrape Cochrane ---
    setLoadingScrape(true);
    try {
      const response = await axios.post("http://127.0.0.1:5000/api/scrape-cochrane", { topic: query });
      setScrapedRecords(response.data.records);
    } catch (error) {
      console.error("Error scraping Cochrane:", error);
      setScrapedRecords([]);
    }
    setLoadingScrape(false);
    };

  return (
    <div className="app-container">
      {/* Big centered container with the title and form */}
      <div className="big-container">
        <h1 className="big-title">SLR Automation Platform</h1>
        <Form onSubmit={handleFormSubmit} />
      </div>

      {/* LLM results */}
      <div className="results-container">
        {/* Research Questions */}
        {loadingQuestions && (
          <div className="loading">Loading research questions...</div>
        )}
        {!loadingQuestions && researchQuestions.length > 0 && (
          <div className="small-container">
            <h2>Research Questions</h2>
            <ResearchQuestions data={researchQuestions} />
          </div>
        )}
        {!loadingQuestions && researchQuestions.length === 0 && (
          <div className="small-container placeholder">
            No research questions found.
          </div>
        )}

        {/* Research Queries */}
        {loadingQueries && (
          <div className="loading">Loading search queries...</div>
        )}
        {!loadingQueries && researchQueries.length > 0 && (
          <div className="small-container">
            <h2>Search Queries</h2>
            <ResearchQueries data={researchQueries} />
          </div>
        )}
        {!loadingQueries && researchQueries.length === 0 && researchQuestions.length > 0 && (
          <div className="small-container placeholder">
            No search queries found.
          </div>
        )}
      </div>

      {/* Scraper results */}
      <div className="results-container">
        {loadingScrape && (
          <div className="loading">Scraping Cochrane...</div>
        )}
        {!loadingScrape && scrapedRecords.length > 0 && (
          <div className="small-container">
            <h2>Cochrane Scrape Results</h2>
            <ScraperResultsTable records={scrapedRecords} />
          </div>
        )}
        {!loadingScrape && scrapedRecords.length === 0 && (
          <div className="small-container placeholder">
            No scraped records found.
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
