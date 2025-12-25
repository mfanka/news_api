import api from "../api/api";

function NewsList({ news, loadNews }) {
  const deleteNews = async (id) => {
    await api.delete(`/news/${id}`);
    loadNews();
  };

  return (
    <div className="row">
      {news.map(item => (
        <div className="col-md-4 mb-3" key={item.id}>
          <div className="card h-100">
            <div className="card-body">
              <h5>{item.title}</h5>
              <p>{item.content.slice(0, 100)}...</p>
              <p><b>Автор:</b> {item.author}</p>
              <button
                className="btn btn-danger btn-sm"
                onClick={() => deleteNews(item.id)}
              >
                Удалить
              </button>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}

export default NewsList;
