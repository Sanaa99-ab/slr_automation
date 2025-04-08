import React, { useState } from 'react';
import axios from 'axios';
import './form.css';

interface FormProps {
  // onSubmit receives two arguments: the results and the query string
  onSubmit: (result: any, query: string) => void;
}

const Form: React.FC<FormProps> = ({ onSubmit }) => {
  const [topic, setTopic] = useState("");
  const [loading, setLoading] = useState(false);

  // Called when the user submits the form.
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      // Post the query to the FastAPI endpoint.
      // Axios will send a JSON body by default.
      //const response = await axios.post("http://127.0.0.1:5000/generate", { topic });
      const response = await axios.post("http://127.0.0.1:5000/api/generate", { topic });

      // Pass the results and current query back to App.
      onSubmit(response.data, topic);
    } catch (error) {
      console.error("Error submitting form:", error);
    }
    setLoading(false);
  };

  return (
    <form onSubmit={handleSubmit} className="form-container">
      <div className="form-group">
        <label htmlFor="topic">Topic:</label>
        <input 
          id="topic"
          type="text" 
          value={topic} 
          onChange={(e) => setTopic(e.target.value)} 
          className="form-control"
          placeholder="Enter research topic..."
        />
      </div>
      <button type="submit" className="btn btn-primary">
        {loading ? "Loading..." : "Submit"}
      </button>
    </form>
  );
};

export default Form;
