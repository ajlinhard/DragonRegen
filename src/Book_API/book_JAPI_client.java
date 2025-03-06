
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import com.google.gson.Gson;
import java.io.IOException;

public class BookAPIClient {
    private final String baseUrl;
    private final HttpClient httpClient;
    private final Gson gson;

    public BookAPIClient(String baseUrl) {
        this.baseUrl = baseUrl;
        this.httpClient = HttpClient.newHttpClient();
        this.gson = new Gson();
    }

    public String getAllBooks() throws IOException, InterruptedException {
        HttpRequest request = HttpRequest.newBuilder()
            .uri(URI.create(baseUrl + "/books"))
            .GET()
            .build();
        
        HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
        return response.body();
    }

    public String getBook(int bookId) throws IOException, InterruptedException {
        HttpRequest request = HttpRequest.newBuilder()
            .uri(URI.create(baseUrl + "/books/" + bookId))
            .GET()
            .build();
        
        HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
        return response.body();
    }

    public String createBook(Book book) throws IOException, InterruptedException {
        String jsonBook = gson.toJson(book);
        
        HttpRequest request = HttpRequest.newBuilder()
            .uri(URI.create(baseUrl + "/books"))
            .header("Content-Type", "application/json")
            .POST(HttpRequest.BodyPublishers.ofString(jsonBook))
            .build();
        
        HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
        return response.body();
    }

    public String updateBook(int bookId, Book book) throws IOException, InterruptedException {
        String jsonBook = gson.toJson(book);
        
        HttpRequest request = HttpRequest.newBuilder()
            .uri(URI.create(baseUrl + "/books/" + bookId))
            .header("Content-Type", "application/json")
            .PUT(HttpRequest.BodyPublishers.ofString(jsonBook))
            .build();
        
        HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
        return response.body();
    }

    public boolean deleteBook(int bookId) throws IOException, InterruptedException {
        HttpRequest request = HttpRequest.newBuilder()
            .uri(URI.create(baseUrl + "/books/" + bookId))
            .DELETE()
            .build();
        
        HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
        return response.statusCode() == 204;
    }

    // Book model class
    public static class Book {
        private int id;
        private String title;
        private String author;
        private String isbn;

        // Constructors, getters, and setters
        public Book(String title, String author, String isbn) {
            this.title = title;
            this.author = author;
            this.isbn = isbn;
        }
    }

    // Example usage
    public static void main(String[] args) {
        try {
            BookAPIClient client = new BookAPIClient("http://localhost:5000");
            
            // Get all books
            String allBooks = client.getAllBooks();
            System.out.println("All Books: " + allBooks);
            
            // Create a new book
            Book newBook = new Book("Dune", "Frank Herbert", "9780441172719");
            String createdBook = client.createBook(newBook);
            System.out.println("Created Book: " + createdBook);
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}