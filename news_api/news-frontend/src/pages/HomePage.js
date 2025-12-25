import { useEffect, useState } from "react";
import api from "../api/api";
import NewsList from "../components/NewsList";
import NewsFilter from "../components/NewsFilter";

function HomePage() {
  const [news, setNews] = useState([]);

  const loadNews = async () => {
    const res = await api.get("/news");
    setNews(res.data.items);
  };

  useEffect(() => {
    loadNews();
  }, []);

  return (
    <>
      <NewsFilter setNews={setNews} />
      <NewsList news={news} loadNews={loadNews} />
    </>
  );
}

export default HomePage;
