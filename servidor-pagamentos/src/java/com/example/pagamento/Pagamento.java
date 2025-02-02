package com.example.pagamento;

import java.rmi.Remote;
import java.rmi.RemoteException;

public interface Pagamento extends Remote {
    String processarPagamento(String orderId, double valor) throws RemoteException;
}