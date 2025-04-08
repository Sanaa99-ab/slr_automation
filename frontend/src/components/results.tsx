// import React from 'react';

// interface ResultsProps {
//   data: {
//     questions: string[];
//     queries: string[];
//     databases: string[];
//     criteria: string[];
//     papers: { id: string; abstract: string }[];
//   } | null;
// }

// const Results: React.FC<ResultsProps> = ({ data }) => {
//   if (!data) return null;

//   return (
//     <div>
//       <div className="card mb-3">
//         <div className="card-body">
//           <h3 className="card-title">Research Questions</h3>
//           <ul className="list-group list-group-flush">
//             {data.questions.map((q, i) => <li key={i} className="list-group-item">{q}</li>)}
//           </ul>
//         </div>
//       </div>
//       <div className="card mb-3">
//         <div className="card-body">
//           <h3 className="card-title">Search Queries</h3>
//           <ul className="list-group list-group-flush">
//             {data.queries.map((q, i) => <li key={i} className="list-group-item">{q}</li>)}
//           </ul>
//         </div>
//       </div>
//       <div className="card mb-3">
//         <div className="card-body">
//           <h3 className="card-title">Selected Databases</h3>
//           <ul className="list-group list-group-flush">
//             {data.databases.map((db, i) => <li key={i} className="list-group-item">{db}</li>)}
//           </ul>
//         </div>
//       </div>
//       <div className="card mb-3">
//         <div className="card-body">
//           <h3 className="card-title">Proposed Criteria</h3>
//           <ul className="list-group list-group-flush">
//             {data.criteria.map((c, i) => <li key={i} className="list-group-item">{c}</li>)}
//           </ul>
//         </div>
//       </div>
//       <div className="card">
//         <div className="card-body">
//           <h3 className="card-title">Scraped Papers (Sample from PubMed)</h3>
//           <ul className="list-group list-group-flush">
//             {data.papers.map((p, i) => <li key={i} className="list-group-item">PMID: {p.id} - {p.abstract}</li>)}
//           </ul>
//         </div>
//       </div>
//     </div>
//   );
// };

// export default Results;

import React from 'react';
import './results.css';

interface ResultsProps {
  data: any;
}

const Results: React.FC<ResultsProps> = ({ data }) => {
  if (!data) {
    return (
      <div className="results-container">
        No results yet. Please submit a query.
      </div>
    );
  }

  return (
    <div className="results-container">
      <h2>Results</h2>
      <div className="result-item">
         {/* Customize how your results are displayed */}
         <pre>{JSON.stringify(data, null, 2)}</pre>
      </div>
    </div>
  );
};

export default Results;
