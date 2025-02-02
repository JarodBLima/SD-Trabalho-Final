package com.example;

import com.example.pagamento.Pagamento;
import com.example.pagamento.PagamentoImpl;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

import java.rmi.registry.LocateRegistry;
import java.rmi.registry.Registry;

public class Main {
    private static final Logger logger = LogManager.getLogger(Main.class);

    public static void main(String[] args) {
        try {
            PagamentoImpl obj = new PagamentoImpl();
            Registry registry = LocateRegistry.createRegistry(1099); // Porta padrão do RMI
            registry.bind("PagamentoService", obj);
            logger.info("Servidor de Pagamentos pronto.");
        } catch (Exception e) {
            logger.error("Erro no servidor: " + e.getMessage());
            e.printStackTrace();
        }
    }
}