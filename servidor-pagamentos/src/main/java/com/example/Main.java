package com.example;

import com.example.pagamento.Pagamento;
import com.example.pagamento.PagamentoImpl;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

import java.rmi.registry.LocateRegistry;
import java.rmi.registry.Registry;
import java.rmi.server.UnicastRemoteObject; // Importe esta classe
import java.rmi.RemoteException;


public class Main {
    private static final Logger logger = LogManager.getLogger(Main.class);

    public static void main(String[] args) {
        try {

             // Configurar o SSL para RMI
            System.setProperty("javax.rmi.ssl.client.enabledProtocols", "TLSv1.2"); // Exemplo, ajuste se necessário
           // System.setProperty("javax.net.ssl.keyStore", "path/to/your/keystore.jks");
           // System.setProperty("javax.net.ssl.keyStorePassword", "your_keystore_password");
           // System.setProperty("javax.net.ssl.trustStore", "path/to/your/truststore.jks");
           // System.setProperty("javax.net.ssl.trustStorePassword", "your_truststore_password");
            //System.setProperty("java.rmi.server.hostname", "servidor-pagamentos"); // Importante para RMI em Docker


            PagamentoImpl obj = new PagamentoImpl();
            //Pagamento stub = (Pagamento) UnicastRemoteObject.exportObject(obj, 0); // Exporte o objeto, se necessário

            Registry registry = LocateRegistry.createRegistry(1099); // Porta padrão do RMI
            registry.bind("PagamentoService", obj);
            logger.info("Servidor de Pagamentos pronto.");
        } catch (Exception e) {
            logger.error("Erro no servidor: " + e.getMessage());
            e.printStackTrace();
        }
    }
}