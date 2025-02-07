package com.example.pagamento;

import java.rmi.RemoteException;
import java.rmi.server.UnicastRemoteObject;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

public class PagamentoImpl extends UnicastRemoteObject implements Pagamento {
    private static final Logger logger = LogManager.getLogger(PagamentoImpl.class);

    public PagamentoImpl() throws RemoteException {
        super();
    }

    @Override
    public String processarPagamento(String orderId, double valor) throws RemoteException {
        // Simular processamento de pagamento
        logger.info("Processando pagamento para o pedido: " + orderId + ", valor: " + valor);

        // Adicionar validações
        if (orderId == null || orderId.trim().isEmpty()) {
            logger.error("ID do pedido inválido.");
            throw new RemoteException("ID do pedido inválido.");
        }
        if (valor <= 0) {
            logger.error("Valor do pagamento inválido.");
            throw new RemoteException("Valor do pagamento inválido.");
        }

        // Simular diferentes cenários (aprovado/reprovado) com base no valor
        String status;
        if (valor > 100) {
            status = "Reprovado";
            logger.info("Pagamento reprovado para o pedido: " + orderId);
        } else {
            status = "Aprovado";
            logger.info("Pagamento aprovado para o pedido: " + orderId);
        }

        return status;
    }
}