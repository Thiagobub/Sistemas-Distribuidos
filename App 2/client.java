
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
        sc = new Scanner(System.in); //System.in is a standard input stream  
        System.out.print("Informe seu nome: ");  
        name = sc.nextLine();              //reads string

        // GET
        Map<Object, Object> data = new HashMap<>();
        data.put("user", name);
        data.put("enquete", "Bonde de Floripa");

        httpclient = HttpClient.newHttpClient();
        httprequest = HttpRequest.newBuilder()
            .GET()
            .uri(URI.create(uri + "?" + buildFormDataFromMap(data)))
            .build();
        System.out.println(uri + "?" + buildFormDataFromMap(data));
        Void response = httpclient.sendAsync(httprequest, BodyHandlers.ofString())
            .thenApply(HttpResponse::body)
            .thenAccept(System.out::println)
            .join();

        System.out.println(response);

        // PUT
        /*
        Map<Object, Object> data = new HashMap<>();
        data.put("user", name);
        data.put("enquete", "Bonde de Floripa");
        data.put("voto", "2021-11-19");

        httpclient = HttpClient.newHttpClient();
        httprequest = HttpRequest.newBuilder()
            .PUT(HttpRequest.BodyPublishers.ofString(buildFormDataFromMap(data)))
            .uri(URI.create(uri))
            .header("Content-Type", "application/x-www-form-urlencoded")
            .build();
        System.out.println(httprequest);
        Void response = httpclient.sendAsync(httprequest, BodyHandlers.ofString())
            .thenApply(HttpResponse::body)
            .thenAccept(System.out::println)
            .join();

        System.out.println(response);   */


        // POST
        /*
        Map<Object, Object> data = new HashMap<>();
        data.put("user", name);
        data.put("enquete", "Nova enquete");
        data.put("local", "Nova York");
        data.put("limite", "2021-12-24");
        data.put("votos", "['2021-11-19','2021-11-20','2021-11-21']");

        httpclient = HttpClient.newHttpClient();
        httprequest = HttpRequest.newBuilder()
            .POST(HttpRequest.BodyPublishers.ofString(buildFormDataFromMap(data)))
            .uri(URI.create(uri))
            .header("Content-Type", "application/x-www-form-urlencoded")
            .build();
        System.out.println(httprequest);
        Void response = httpclient.sendAsync(httprequest, BodyHandlers.ofString())
            .thenApply(HttpResponse::body)
            .thenAccept(System.out::println)
            .join();

        System.out.println(response);   */

        return;
    }

    private void send_info(){
        /// jogar a parte de cima aqui dentro pra não ficar tão repetido
    }

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
        System.out.println("Acessando o sistema.");

        System.out.println(name);
        // FAZER VISITA AO SERVER ENVIANDO O TEU NOME

        while (true) {
            System.out.println("1 - Cadastrar enquete\n2 - Cadastrar voto em enquete\n3 - Consultar enquete\n");
            System.out.println("Escolha uma das opções acima: ");
            int n = sc.nextInt();
            sc.nextLine();

            if (n == 1) {
                System.out.println("Informe o titulo da enquete: ");
                String titulo = sc.nextLine();
                System.out.println("Informe o local do evento: ");
                String local = sc.nextLine();
                System.out.println("Informe datas e horários possíveis do evento (yyyy-mm-dd_hh:mm, yyyy-mm-dd_hh:mm, ...): ");
                String tempo = sc.nextLine();
                System.out.println("Informe data limite de votação (yyyy-mm-dd_hh:mm): ");
                String limite = sc.nextLine();

                System.out.println(name + titulo + local + tempo + limite);
                // Enviar infos pro servidor

            } else if (n == 2) {
                System.out.println("Informe o titulo da enquete: ");
                String titulo = sc.nextLine();
                System.out.println("Informe data e horário que deseja participar (yyyy-mm-dd_hh:mm): ");
                String tempo = sc.nextLine();

                System.out.println(name + titulo + tempo);
                // Enviar infos pro servidor

            } else if (n == 3) {
                System.out.println("Informe o titulo da enquete: ");
                String titulo = sc.nextLine();

                System.out.println(name + titulo);
                // Enviar infos pro servidor

            }
        }
    }


    public static void main(String[] args) {
        
        client user = new client();
        user.start();
    }
}