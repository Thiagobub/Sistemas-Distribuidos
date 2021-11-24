import java.net.URI;
import java.net.URLEncoder;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.net.http.HttpResponse.BodyHandlers;
import java.nio.charset.StandardCharsets;
import java.util.HashMap;
import java.util.Map;
import java.util.Scanner;


public class client {

    String name;
    int abort;
    Scanner sc;

    HttpClient httpclient;
    HttpRequest httprequest;

    String uri = "http://127.0.0.1:5000/users";

    public client() {

        sc = new Scanner(System.in);                //System.in is a standard input stream  
        System.out.print("Informe seu nome: ");  
        name = sc.nextLine();                       //reads string

        // GET - visit
        Map<Object, Object> data = new HashMap<>();
        data.put("user", name);
        data.put("request", "visit");

        httpclient = HttpClient.newHttpClient();
        httprequest = HttpRequest.newBuilder()
            .GET()
            .uri(URI.create(uri + "?" + buildFormDataFromMap(data)))
            .build();
        //System.out.println(uri + "?" + buildFormDataFromMap(data));
        Void response = httpclient.sendAsync(httprequest, BodyHandlers.ofString())
            .thenApply(HttpResponse::body)
            .thenAccept(System.out::println)
            .join();

        //System.out.println(response);
        return;
    }

    private void send_info(){
        /// jogar a parte de cima aqui dentro pra não ficar tão repetido
    }

    // public interface EventHandler {

    //     /**
    //      * Handle the event text.
    //      * @param eventText - trimmed event text
    //      */
    //     public void handle(String eventText);
    // }

    //private static HttpRequest.BodyPublisher buildFormDataFromMap(Map<Object, Object> data) {
    private static String buildFormDataFromMap(Map<Object, Object> data) {
        var builder = new StringBuilder();
        for (Map.Entry<Object, Object> entry : data.entrySet()) {
            if (builder.length() > 0) {
                builder.append("&");
            }
            builder.append(URLEncoder.encode(entry.getKey().toString(), StandardCharsets.UTF_8));
            builder.append("=");
            builder.append(URLEncoder.encode(entry.getValue().toString(), StandardCharsets.UTF_8));
        }
        //return HttpRequest.BodyPublishers.ofString(builder.toString());
        return builder.toString();
    }

    public void start() {
        //System.out.println("Acessando o sistema.");

        //System.out.println(name);
        // FAZER VISITA AO SERVER ENVIANDO O TEU NOME

        while (true) {
            System.out.println("1 - Cadastrar enquete\n2 - Cadastrar voto em enquete\n3 - Consultar enquete\n");
            System.out.println("Escolha uma das opcoes acima: ");
            int n = sc.nextInt();
            sc.nextLine();

            if (n == 1) {
                System.out.println("Informe o titulo da enquete: ");
                String titulo = sc.nextLine();
                System.out.println("Informe o local do evento: ");
                String local = sc.nextLine();
                System.out.println("Informe datas e horarios possiveis do evento (yyyy-mm-dd_hh:mm, yyyy-mm-dd_hh:mm, ...): ");
                String tempo = sc.nextLine();
                System.out.println("Informe data limite de votacao (yyyy-mm-dd_hh:mm): ");
                String limite = sc.nextLine();

                //System.out.println(name + titulo + local + tempo + limite);

                // Enviar infos pro servidor
                Map<Object, Object> data = new HashMap<>();
                data.put("user", name);
                data.put("enquete", titulo);
                data.put("local", local);
                data.put("limite", limite);
                data.put("votos", tempo);
        
                httpclient = HttpClient.newHttpClient();
                httprequest = HttpRequest.newBuilder()
                    .POST(HttpRequest.BodyPublishers.ofString(buildFormDataFromMap(data)))
                    .uri(URI.create(uri))
                    .header("Content-Type", "application/x-www-form-urlencoded")
                    .build();
                //System.out.println(httprequest);
                Void response = httpclient.sendAsync(httprequest, BodyHandlers.ofString())
                    .thenApply(HttpResponse::body)
                    .thenAccept(System.out::println)
                    .join();
        
                //System.out.println(response);
                

            } else if (n == 2) {
                Map<Object, Object> data = new HashMap<>();
                data.put("user", name);
                
                System.out.println("Informe o titulo da enquete: ");
                String titulo = sc.nextLine();
                data.put("enquete", titulo);
                
                System.out.println("Informe data e horario que deseja participar (yyyy-mm-dd_hh:mm): ");
                String tempo = sc.nextLine();

                //System.out.println(name + titulo + tempo);

                // Enviar infos pro servidor
                //Map<Object, Object> data = new HashMap<>();
                //data.put("user", name);
                data.put("enquete", titulo);
                data.put("voto", tempo);
        
                httpclient = HttpClient.newHttpClient();
                httprequest = HttpRequest.newBuilder()
                    .PUT(HttpRequest.BodyPublishers.ofString(buildFormDataFromMap(data)))
                    .uri(URI.create(uri))
                    .header("Content-Type", "application/x-www-form-urlencoded")
                    .build();
                //System.out.println(httprequest);
                Void response = httpclient.sendAsync(httprequest, BodyHandlers.ofString())
                    .thenApply(HttpResponse::body)
                    .thenAccept(System.out::println)
                    .join();
        
                //System.out.println(response);

            } else if (n == 3) {
                System.out.println("Informe o titulo da enquete: ");
                String titulo = sc.nextLine();

                //System.out.println(name + titulo);

                // Enviar infos pro servidor
                Map<Object, Object> data = new HashMap<>();
                data.put("user", name);
                data.put("enquete", titulo);
                data.put("request", "get info");

                httpclient = HttpClient.newHttpClient();
                httprequest = HttpRequest.newBuilder()
                    .GET()
                    .uri(URI.create(uri + "?" + buildFormDataFromMap(data)))
                    .build();
                //System.out.println(uri + "?" + buildFormDataFromMap(data));
                Void response = httpclient.sendAsync(httprequest, BodyHandlers.ofString())
                    .thenApply(HttpResponse::body)
                    .thenAccept(System.out::println)
                    .join();

                //System.out.println(response);
            }
        }
    }


    public static void main(String[] args) {
        
        client user = new client();
        user.start();
    }
}
