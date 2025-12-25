import { useState } from "react";
import api from "../api/api";

function NewsFilter({ setNews }) {
  const [query, setQuery] = useState("");

  const search = async () => {
    const res = await api.get(`/news?q=${query}`);
    setNews(res.data.items);
  };

  return (
    <div className="mb-3">
      <input
        className="form-control"
        placeholder="Поиск по ключевому слову"
        onChange={e => setQuery(e.target.value)}
      />
      <button className="btn btn-secondary mt-2" onClick={search}>
        Найти
      </button>
    </div>
  );
}

export default NewsFilter;
