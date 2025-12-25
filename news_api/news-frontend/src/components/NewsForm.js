import { useEffect, useState } from "react";
import api from "../api/api";

function NewsForm() {
  const [categories, setCategories] = useState([]);

  const [form, setForm] = useState({
    title: "",
    content: "",
    author: "",
    category_id: "",
    is_published: true
  });

  // загрузка категорий
  useEffect(() => {
    const loadCategories = async () => {
      const res = await api.get("/categories");
      setCategories(res.data);
    };
    loadCategories();
  }, []);

  const submit = async (e) => {
    e.preventDefault();

    if (
      form.title.length < 5 ||
      form.content.length < 20 ||
      form.author.length < 2 ||
      !form.category_id
    ) {
      alert("Заполни все поля корректно!");
      return;
    }

    try {
      await api.post("/news", {
        ...form,
        category_id: Number(form.category_id)
      });
      alert("Новость успешно добавлена!");

      setForm({
        title: "",
        content: "",
        author: "",
        category_id: "",
        is_published: true
      });
    } catch (err) {
      alert("Ошибка при добавлении новости");
      console.error(err);
    }
  };

  return (
    <form onSubmit={submit}>
      <input
        className="form-control mb-2"
        placeholder="Заголовок"
        value={form.title}
        onChange={e => setForm({ ...form, title: e.target.value })}
      />

      <textarea
        className="form-control mb-2"
        placeholder="Текст новости (минимум 20 символов)"
        value={form.content}
        onChange={e => setForm({ ...form, content: e.target.value })}
      />

      <input
        className="form-control mb-2"
        placeholder="Автор"
        value={form.author}
        onChange={e => setForm({ ...form, author: e.target.value })}
      />

      <select
        className="form-control mb-3"
        value={form.category_id}
        onChange={e => setForm({ ...form, category_id: e.target.value })}
      >
        <option value="">Выберите категорию</option>
        {categories.map(cat => (
          <option key={cat.id} value={cat.id}>
            {cat.name}
          </option>
        ))}
      </select>

      <button className="btn btn-primary">
        Добавить новость
      </button>
    </form>
  );
}

export default NewsForm;
